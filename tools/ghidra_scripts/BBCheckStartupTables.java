// Independent switch recovery for the two startup libc code/data disputes.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.pcode.*;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
public class BBCheckStartupTables extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();Path out=Path.of(args[1]);
  JsonObject input=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
  for(JsonElement e:input.getAsJsonArray("segments")){
   JsonObject s=e.getAsJsonObject();byte[] b=Files.readAllBytes(Path.of(s.get("path").getAsString()));
   MemoryBlock block=currentProgram.getMemory().createInitializedBlock(s.get("name").getAsString(),toAddr(s.get("rva").getAsLong()),new ByteArrayInputStream(b),b.length,monitor,false);
   block.setExecute(true);block.setWrite(false);
  }
  // Shared ABI contract only; no switch bounds or destinations are supplied.
  Address abort=toAddr(input.get("abort_rva").getAsLong());disassemble(abort);createFunction(abort,"verified_libc_abort");getFunctionAt(abort).setNoReturn(true);
  for(JsonElement e:input.getAsJsonArray("entries")){Address a=toAddr(e.getAsLong());disassemble(a);createFunction(a,"startup_switch_"+a);}
  analyzeAll(currentProgram);
  DecompInterface decompiler=new DecompInterface();JsonArray output=new JsonArray();
  try{
   if(!decompiler.openProgram(currentProgram))throw new IOException(decompiler.getLastMessage());
   for(JsonElement e:input.getAsJsonArray("entries")){
    long start=e.getAsLong();Function function=getFunctionAt(toAddr(start));
    DecompileResults result=decompiler.decompileFunction(function,90,monitor);
    if(!result.decompileCompleted())throw new IOException(result.getErrorMessage());
    Files.writeString(out.resolve(Long.toHexString(start)+".c"),result.getDecompiledFunction().getC());
    JsonObject row=new JsonObject();row.addProperty("entry",start);JsonArray tables=new JsonArray();
    for(JumpTable table:result.getHighFunction().getJumpTables()){
     JsonObject t=new JsonObject();t.addProperty("branch",table.getSwitchAddress().getOffset());JsonArray targets=new JsonArray();
     for(Address a:table.getCases())targets.add(a.getOffset());t.add("targets",targets);tables.add(t);
    }
    JsonArray instructions=new JsonArray();InstructionIterator it=currentProgram.getListing().getInstructions(function.getBody(),true);
    while(it.hasNext()){
     Instruction i=it.next();JsonObject r=new JsonObject();r.addProperty("rva",i.getAddress().getOffset());r.addProperty("length",i.getLength());
     StringBuilder hex=new StringBuilder();for(byte b:i.getBytes())hex.append(String.format("%02x",b&255));r.addProperty("bytes",hex.toString());r.addProperty("text",i.toString());instructions.add(r);
    }
    row.add("tables",tables);row.add("instructions",instructions);output.add(row);
   }
  }finally{decompiler.dispose();}
  Files.writeString(out.resolve("ghidra.json"),new GsonBuilder().setPrettyPrinting().create().toJson(output));
 }
}
