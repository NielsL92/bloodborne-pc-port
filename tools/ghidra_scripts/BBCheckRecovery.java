// Independent recursive SLEIGH decode, restricted only by an analysis window.
// No expected instruction addresses or branch targets are supplied.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
public class BBCheckRecovery extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();
  JsonObject input=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
  for(JsonElement e:input.getAsJsonArray("segments")){
   JsonObject s=e.getAsJsonObject();byte[] b=Files.readAllBytes(Path.of(s.get("path").getAsString()));
   MemoryBlock block=currentProgram.getMemory().createInitializedBlock(s.get("name").getAsString(),toAddr(s.get("rva").getAsLong()),new ByteArrayInputStream(b),b.length,monitor,false);
   block.setExecute(true);block.setWrite(false);
  }
  JsonArray output=new JsonArray();
  for(JsonElement e:input.getAsJsonArray("entries")){
   JsonObject s=e.getAsJsonObject();long start=s.get("start").getAsLong(),end=s.get("end").getAsLong();
   AddressSet window=new AddressSet(toAddr(start),toAddr(end-1));
   currentProgram.getListing().clearCodeUnits(toAddr(start),toAddr(end-1),false);
   Disassembler dis=Disassembler.getDisassembler(currentProgram,monitor,null);
   dis.disassemble(toAddr(start),window,true);
   if(s.has("additional_roots"))for(JsonElement root:s.getAsJsonArray("additional_roots")){
    Address address=toAddr(root.getAsLong());
    if(!window.contains(address))throw new IllegalArgumentException("LSDA root outside analysis window");
    dis.disassemble(address,window,true);
   }
   JsonArray rows=new JsonArray();InstructionIterator it=currentProgram.getListing().getInstructions(window,true);
   while(it.hasNext()){
    Instruction ins=it.next();JsonObject r=new JsonObject();r.addProperty("rva",ins.getAddress().getOffset());r.addProperty("length",ins.getLength());
    StringBuilder hex=new StringBuilder();for(byte b:ins.getBytes())hex.append(String.format("%02x",b&255));
    r.addProperty("bytes",hex.toString());r.addProperty("text",ins.toString());r.addProperty("flow",ins.getFlowType().toString());
    JsonArray targets=new JsonArray();for(Address a:ins.getFlows())targets.add(a.getOffset());r.add("targets",targets);rows.add(r);
   }
   JsonObject result=new JsonObject();result.addProperty("start",start);result.addProperty("end",end);result.add("instructions",rows);output.add(result);
  }
  Files.writeString(Path.of(args[1]),new GsonBuilder().setPrettyPrinting().create().toJson(output));
  println("BB_RECOVERY checked="+output.size());
 }
}
