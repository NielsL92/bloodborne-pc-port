// Independent decoder and decompiler view of the pinned initializer.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
public class BBCheckStartup extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        Path source=Path.of(args[0]),out=Path.of(args[1]);
        JsonObject facts=JsonParser.parseString(Files.readString(source.resolve("summary.json"))).getAsJsonObject();
        byte[] global=Files.readAllBytes(source.resolve("globals-relocated.bin"));
        MemoryBlock block=currentProgram.getMemory().createInitializedBlock("initial_relocated_globals",
            toAddr(facts.getAsJsonObject("analysis_globals").get("start").getAsLong()),
            new ByteArrayInputStream(global),global.length,monitor,false);
        block.setWrite(false);block.setExecute(false);
        disassemble(toAddr(0x20));createFunction(toAddr(0x20),"game_initializers");
        Function function=getFunctionAt(toAddr(0x20));
        DecompInterface decompiler=new DecompInterface();
        JsonArray instructions=new JsonArray(),calls=new JsonArray();
        InstructionIterator it=currentProgram.getListing().getInstructions(function.getBody(),true);
        while(it.hasNext()){
            Instruction ins=it.next();JsonObject row=new JsonObject();row.addProperty("rva",ins.getAddress().getOffset());
            row.addProperty("length",ins.getLength());
            StringBuilder hex=new StringBuilder();for(byte b:ins.getBytes())hex.append(String.format("%02x",b&255));
            row.addProperty("bytes",hex.toString());instructions.add(row);
            if(ins.getFlowType().isCall()&&ins.getFlowType().isComputed())calls.add(ins.getAddress().getOffset());
        }
        try{
            if(!decompiler.openProgram(currentProgram))throw new IOException(decompiler.getLastMessage());
            DecompileResults result=decompiler.decompileFunction(function,60,monitor);
            if(!result.decompileCompleted())throw new IOException(result.getErrorMessage());
            Files.writeString(out.resolve("decompiled.c"),result.getDecompiledFunction().getC());
        }finally{decompiler.dispose();}
        JsonObject result=new JsonObject();result.add("instructions",instructions);result.add("indirect_call_sites",calls);
        Files.writeString(out.resolve("ghidra.json"),new GsonBuilder().setPrettyPrinting().create().toJson(result));
        println("BB_RESEARCH initializer instructions="+instructions.size()+" indirect calls="+calls.size());
    }
}
