// Cross-check supplied exception metadata using Ghidra's independent CIE/FDE/LSDA readers.
// @category BloodborneResearch
import ghidra.app.script.GhidraScript;
import ghidra.app.plugin.exceptionhandlers.gcc.*;
import ghidra.app.plugin.exceptionhandlers.gcc.sections.*;
import ghidra.app.plugin.exceptionhandlers.gcc.structures.ehFrame.*;
import ghidra.app.plugin.exceptionhandlers.gcc.structures.gccexcepttable.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;

public class BBCheckExceptions extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=2)throw new IllegalArgumentException("manifest and output JSON required");
        JsonObject input=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        for(JsonElement e:input.getAsJsonArray("segments")){
            JsonObject s=e.getAsJsonObject();
            byte[] bytes=Files.readAllBytes(Path.of(s.get("path").getAsString()));
            MemoryBlock block=currentProgram.getMemory().createInitializedBlock(
                s.get("name").getAsString(),toAddr(s.get("rva").getAsLong()),
                new ByteArrayInputStream(bytes),bytes.length,monitor,false);
            block.setRead(true);block.setWrite(false);block.setExecute(false);
        }
        Map<Address,Cie> cies=new HashMap<>();
        CieSource source=address->{
            Cie c=cies.get(address);
            if(c==null){c=new Cie(monitor,currentProgram);c.create(address);cies.put(address,c);}
            return c;
        };
        JsonArray results=new JsonArray();
        for(JsonElement e:input.getAsJsonArray("fdes")){
            long fdeAddress=e.getAsLong();
            FrameDescriptionEntry fde=new FrameDescriptionEntry(monitor,currentProgram,source);
            RegionDescriptor region=fde.create(toAddr(fdeAddress));
            if(region==null)throw new IOException("null FDE region at "+Long.toHexString(fdeAddress));
            JsonObject row=new JsonObject();
            row.addProperty("fde",fdeAddress);
            row.addProperty("start",region.getRangeStart().getOffset());
            row.addProperty("size",region.getRangeSize());
            Address lsda=region.getLSDAAddress(toAddr(fdeAddress));
            if(lsda==null)throw new IOException("missing LSDA at "+Long.toHexString(fdeAddress));
            row.addProperty("lsda",lsda.getOffset());
            LSDATable table=region.getLSDATable();
            if(table==null){
                table=new LSDATable(monitor,currentProgram);
                region.setLSDATable(table);
                table.create(lsda,region);
            }
            JsonArray calls=new JsonArray();
            for(LSDACallSiteRecord c:table.getCallSiteTable().getCallSiteRecords()){
                JsonObject call=new JsonObject();
                AddressRange range=c.getCallSite();
                call.addProperty("start",range.getMinAddress().getOffset());
                call.addProperty("length",range.getLength());
                if(c.getLandingPadOffset()==0)call.add("landing_pad",JsonNull.INSTANCE);
                else call.addProperty("landing_pad",c.getLandingPad().getOffset());
                call.addProperty("action",c.getActionOffset());
                calls.add(call);
            }
            row.add("call_sites",calls);results.add(row);
        }
        Files.writeString(Path.of(args[1]),new GsonBuilder().serializeNulls().setPrettyPrinting().create().toJson(results));
        println("BB_RESEARCH independent exception regions="+results.size());
    }
}
