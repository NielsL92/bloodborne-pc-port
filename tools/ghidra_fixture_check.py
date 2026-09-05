"""Cross-check the real bit reader with Ghidra's independent decoder/decompiler."""
import hashlib,json,subprocess,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
projects=out/"projects";projects.mkdir()
source=root/"local/compiler-spike/real-jump-v1"
cmd=[sys.executable,"tools/ghidra_headless.py",str(projects),"bitreader",
 "-import",str(source/"original.bin"),"-loader","BinaryLoader","-loader-baseAddr","0x401f0",
 "-processor","x86:LE:64:default","-cspec","gcc","-noanalysis","-max-cpu","2",
 "-scriptPath",str(root/"tools/ghidra_scripts"),"-postScript","BBCheckBitReader.java",
 str(source/"global.bin"),str(out),"-log",str(out/"application.log"),"-scriptlog",str(out/"script.log")]
with (out/"stdout.log").open("wb") as o,(out/"stderr.log").open("wb") as e:
 r=subprocess.run(cmd,stdout=o,stderr=e,timeout=180)
if r.returncode:raise RuntimeError(f"Ghidra exit {r.returncode}; logs preserved")
p=out/"ghidra.json"
if not p.exists():raise RuntimeError("Ghidra script produced no checked result")
data=json.loads(p.read_text());recovery=json.loads((source/"recovery.json").read_text())
assert len(data["tables"])==1 and set(data["tables"][0]["cases"])==set(recovery["targets"]),data["tables"]
raw=(source/"original.bin").read_bytes();decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for ins in data["instructions"]:
 offset=ins["rva"]-0x401f0;actual=raw[offset:offset+ins["length"]]
 assert actual.hex()==ins["bytes"]
 decoded=list(decoder.disasm(actual,ins["rva"]))
 assert len(decoded)==1 and decoded[0].size==ins["length"]
assert all(x["rva"]<0x40378 for x in data["instructions"]),"table decoded as code"
summary=dict(status="pass",ghidra_version="12.1.3",instruction_boundaries_agree=data["instruction_count"],
 independent_jump_targets=data["tables"],raw_sha256=hashlib.sha256(raw).hexdigest(),
 caveat="One bounded function cross-check; decompiled C is evidence for analysis, not automatically trusted compiled source.")
(out/"summary.json").write_bytes((json.dumps(summary,indent=2)+"\n").encode())
print(json.dumps(summary))
