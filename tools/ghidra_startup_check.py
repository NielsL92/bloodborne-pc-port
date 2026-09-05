"""Check the recovered initializer independently without supplying control-flow targets."""
import collections,hashlib,json,subprocess,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM
root=Path.cwd();source=root/"local/cfg/startup-v1";out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
facts=json.loads((source/"summary.json").read_text());raw=(source/"original.bin").read_bytes()
assert hashlib.sha256(raw).hexdigest()==facts["initializer"]["sha256"]
assert hashlib.sha256((source/"globals-relocated.bin").read_bytes()).hexdigest()==facts["analysis_globals"]["sha256"]
projects=out/"projects";projects.mkdir()
command=[sys.executable,"tools/ghidra_headless.py",str(projects),"startup",
 "-import",str(source/"original.bin"),"-loader","BinaryLoader","-loader-baseAddr","0x20",
 "-processor","x86:LE:64:default","-cspec","gcc","-noanalysis","-max-cpu","2",
 "-scriptPath",str(root/"tools/ghidra_scripts"),"-postScript","BBCheckStartup.java",str(source),str(out),
 "-log",str(out/"application.log"),"-scriptlog",str(out/"script.log")]
with (out/"stdout.log").open("wb") as stdout,(out/"stderr.log").open("wb") as stderr:
 r=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=180)
if r.returncode or not (out/"ghidra.json").exists():raise RuntimeError("Ghidra initializer check failed; inspect preserved logs")
actual=json.loads((out/"ghidra.json").read_text())
decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
queue=collections.deque([0x20]);expected={}
while queue:
 address=queue.popleft()
 if address in expected:continue
 assert 0x20<=address<0x91
 ins=next(decoder.disasm(raw[address-0x20:],address,count=1))
 expected[address]=dict(rva=address,length=ins.size,bytes=ins.bytes.hex())
 if ins.group(CS_GRP_RET):continue
 if ins.group(CS_GRP_JUMP):
  assert ins.operands[0].type==X86_OP_IMM
  queue.append(ins.operands[0].imm)
  if ins.mnemonic=="jmp":continue
 queue.append(address+ins.size)
assert {i["rva"]:i for i in actual["instructions"]}==expected
assert actual["indirect_call_sites"]==[0x58,0x82]
summary=dict(status="pass",instructions=len(expected),indirect_call_sites=actual["indirect_call_sites"],
 initializer_sha256=facts["initializer"]["sha256"],limitations="Independent instruction/flow check of the initializer only. Ghidra receives relocation-applied data, not constructor targets as annotations. Constructor coverage, mutations and runtime callback registration remain open.")
(out/"summary.json").write_bytes((json.dumps(summary,indent=2)+"\n").encode())
print(json.dumps(summary),flush=True)
