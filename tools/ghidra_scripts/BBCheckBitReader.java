// Independent Ghidra analysis of the bounded real bit-reader fixture.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.pcode.*;
import java.nio.file.*;
import java.io.*;
public class BBCheckBitReader extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=2)throw new IllegalArgumentException("global bytes, output directory required");
        Path out=Path.of(args[1]);
        byte[] global=Files.readAllBytes(Path.of(args[0]));
        MemoryBlock block=currentProgram.getMemory().createInitializedBlock("verified_lookup",
            toAddr(0x2bc0f50),new ByteArrayInputStream(global),global.length,monitor,false);
        block.setWrite(false);block.setExecute(false);
        disassemble(toAddr(0x401f0));
        createFunction(toAddr(0x401f0),"bit_reader");
        analyzeAll(currentProgram);
        Function function=getFunctionAt(toAddr(0x401f0));
        DecompInterface decompiler=new DecompInterface();
        try {
            if(!decompiler.openProgram(currentProgram))throw new IOException(decompiler.getLastMessage());
            DecompileResults result=decompiler.decompileFunction(function,60,monitor);
            if(!result.decompileCompleted())throw new IOException(result.getErrorMessage());
            Files.writeString(out.resolve("decompiled.c"),result.getDecompiledFunction().getC());
            JumpTable[] tables=result.getHighFunction().getJumpTables();
            StringBuilder json=new StringBuilder("{\"language\":\""+currentProgram.getLanguageID()+"\",\"tables\":[");
            for(int i=0;i<tables.length;i++){
                if(i>0)json.append(",");
                json.append("{\"branch\":\"").append(tables[i].getSwitchAddress()).append("\",\"cases\":[");
                Address[] cases=tables[i].getCases();
                for(int j=0;j<cases.length;j++){if(j>0)json.append(",");json.append(cases[j].getOffset());}
                json.append("]}");
            }
            json.append("],\"instructions\":[");
            InstructionIterator iterator=currentProgram.getListing().getInstructions(function.getBody(),true);
            int count=0;
            while(iterator.hasNext()){
                Instruction ins=iterator.next();
                if(count++>0)json.append(",");
                json.append("{\"rva\":").append(ins.getAddress().getOffset()).append(",\"bytes\":\"");
                for(byte b:ins.getBytes())json.append(String.format("%02x",b&255));
                json.append("\",\"length\":").append(ins.getLength()).append("}");
            }
            json.append("],\"instruction_count\":").append(count).append("}");
            Files.writeString(out.resolve("ghidra.json"),json.toString());
            println("BB_RESEARCH tables="+tables.length+" instructions="+count);
        } finally { decompiler.dispose(); }
    }
}
