// Independent read of bounded table bytes and ELF64 Rela records.
// No expected target addends or decoded source instructions are supplied.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;
import com.google.gson.*;
import java.nio.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;
public class BBCheckObjectDispatchTables extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();JsonObject input=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
  for(JsonElement item:input.getAsJsonArray("tables")){
   JsonObject table=item.getAsJsonObject();long address=table.get("address").getAsLong();byte[] data=Files.readAllBytes(Path.of(table.get("path").getAsString()));
   MemoryBlock block=currentProgram.getMemory().createInitializedBlock("candidate_table_"+Long.toHexString(address),toAddr(address),new ByteArrayInputStream(data),data.length,monitor,false);block.setExecute(false);block.setWrite(false);
  }
  byte[] data=Files.readAllBytes(Path.of(input.get("relocations").getAsString()));if(data.length%24!=0)throw new IOException("Invalid ELF64 Rela table length");
  ByteBuffer bytes=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);Map<Long,long[]> records=new HashMap<>();
  Set<Long> requested=new HashSet<>();for(JsonElement item:input.getAsJsonArray("slots"))requested.add(item.getAsJsonObject().get("slot").getAsLong());
  for(int offset=0;offset<data.length;offset+=24){long slot=bytes.getLong(offset),info=bytes.getLong(offset+8),addend=bytes.getLong(offset+16);
   if(requested.contains(slot)){if(records.containsKey(slot))throw new IOException("Duplicate relocation at requested slot");records.put(slot,new long[]{info&0xffffffffL,info>>>32,addend,offset});}
  }
  JsonArray output=new JsonArray();for(JsonElement item:input.getAsJsonArray("slots")){
   JsonObject spec=item.getAsJsonObject();long slot=spec.get("slot").getAsLong();long[] record=records.get(slot);if(record==null)throw new IOException("Missing relocation at requested slot");
   JsonObject row=new JsonObject();row.addProperty("name",spec.get("name").getAsString());row.addProperty("slot",slot);row.addProperty("raw_word",currentProgram.getMemory().getLong(toAddr(slot)));row.addProperty("type",record[0]);row.addProperty("symbol",record[1]);row.addProperty("addend",record[2]);row.addProperty("relocation_byte_offset",record[3]);output.add(row);
  }
  Files.writeString(Path.of(args[1]),new GsonBuilder().setPrettyPrinting().create().toJson(output));println("BB_OBJECT_DISPATCH_TABLES checked="+output.size());
 }
}
