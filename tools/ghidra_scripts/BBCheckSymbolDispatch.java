// Independent ELF64 symbol/Rela parsing and two-step initial RTTI dispatch.
// No expected symbol index, target address, value, name or addend is supplied.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;
import com.google.gson.*;
import java.nio.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.util.*;
public class BBCheckSymbolDispatch extends GhidraScript {
 ByteBuffer symbols; byte[] strings; Map<Long,long[]> relocs=new HashMap<>();
 JsonObject resolve(long slot,int requiredType) throws Exception {
  long[] r=relocs.get(slot);if(r==null||r[0]!=1)throw new IOException("Missing symbol relocation at slot");
  long index=r[1];if(index<0||index>=symbols.capacity()/24)throw new IOException("Symbol index out of range");
  int off=(int)index*24;long nameOffset=Integer.toUnsignedLong(symbols.getInt(off));
  int info=Byte.toUnsignedInt(symbols.get(off+4));int section=Short.toUnsignedInt(symbols.getShort(off+6));
  long value=symbols.getLong(off+8),size=symbols.getLong(off+16);
  if(section==0||(info&15)!=requiredType)throw new IOException("Undefined symbol or wrong symbol role");
  if(nameOffset>=strings.length)throw new IOException("String offset out of range");
  int end=(int)nameOffset;while(end<strings.length&&strings[end]!=0)end++;
  if(end==strings.length)throw new IOException("Unterminated symbol name");
  String name=new String(strings,(int)nameOffset,end-(int)nameOffset,StandardCharsets.US_ASCII);
  JsonObject out=new JsonObject();out.addProperty("slot",slot);out.addProperty("raw_word",currentProgram.getMemory().getLong(toAddr(slot)));
  out.addProperty("relocation_type",r[0]);out.addProperty("symbol_index",index);out.addProperty("addend",r[2]);out.addProperty("relocation_byte_offset",r[3]);
  out.addProperty("symbol_byte_offset",off);out.addProperty("name_offset",nameOffset);out.addProperty("name",name);out.addProperty("bind",info>>>4);out.addProperty("symbol_type",info&15);out.addProperty("section_index",section);
  out.addProperty("value",value);out.addProperty("size",size);out.addProperty("initial_target",Math.addExact(value,r[2]));return out;
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();JsonObject input=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
  for(JsonElement item:input.getAsJsonArray("segments")){
   JsonObject s=item.getAsJsonObject();long address=s.get("address").getAsLong();byte[] data=Files.readAllBytes(Path.of(s.get("path").getAsString()));
   MemoryBlock block=currentProgram.getMemory().createInitializedBlock("supplied_"+Long.toHexString(address),toAddr(address),new ByteArrayInputStream(data),data.length,monitor,false);block.setExecute(false);block.setWrite(false);
  }
  byte[] bytes=Files.readAllBytes(Path.of(input.get("relocations").getAsString()));if(bytes.length%24!=0)throw new IOException("Invalid Rela extent");
  ByteBuffer rela=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
  for(int off=0;off<bytes.length;off+=24){long slot=rela.getLong(off),info=rela.getLong(off+8),addend=rela.getLong(off+16);if(relocs.put(slot,new long[]{info&0xffffffffL,info>>>32,addend,off})!=null)throw new IOException("Duplicate relocation");}
  symbols=ByteBuffer.wrap(Files.readAllBytes(Path.of(input.get("symbols").getAsString()))).order(ByteOrder.LITTLE_ENDIAN);if(symbols.capacity()%24!=0)throw new IOException("Invalid symbol extent");
  strings=Files.readAllBytes(Path.of(input.get("strings").getAsString()));
  JsonObject first=resolve(input.get("object_slot").getAsLong(),1);long table=first.get("initial_target").getAsLong();
  JsonObject second=resolve(Math.addExact(table,input.get("table_offset").getAsLong()),2);
  JsonArray chain=new JsonArray();chain.add(first);chain.add(second);JsonObject result=new JsonObject();result.add("chain",chain);result.addProperty("target",second.get("initial_target").getAsLong());
  Files.writeString(Path.of(args[1]),new GsonBuilder().setPrettyPrinting().create().toJson(result));println("BB_SYMBOL_DISPATCH checked=2");
 }
}
