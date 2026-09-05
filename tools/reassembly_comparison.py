"""Bounded alternative comparison, explicitly separate from lifted recompilation."""
from pathlib import Path
import hashlib,json,subprocess,statistics
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP
from capstone.x86 import X86_OP_IMM
from tools.formats import ElfImage
from tools.dev import environment,LLVM
root=Path.cwd();out=root/"local/compiler-spike/reassembly-comparison";out.mkdir(parents=True,exist_ok=False)
im=ElfImage((root/"local/update/uroot/eboot.bin").read_bytes());ranges={f["start"]:f for f in im.unwind_functions()}
cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
entries={0x3360:"reassembled_loop",0x2fa30:"reassembled_hash",0x5e4e0:"reassembled_hash_body"}
instructions={}
for rva in entries:
 raw=im.at_va(rva,ranges[rva]["size"]);(out/f"{rva:x}.bin").write_bytes(raw)
 instructions[rva]=list(cs.disasm(raw,rva))
 assert sum(i.size for i in instructions[rva])==len(raw)
known={i.address for group in instructions.values() for i in group}
lines=[".intel_syntax noprefix",".text"]
for rva,symbol in entries.items():
 lines += [".p2align 4",f".globl {symbol}",symbol+":"]
 for i in instructions[rva]:
  assert "rip" not in i.op_str and "fs:" not in i.op_str and "gs:" not in i.op_str
  operand=i.op_str
  if i.group(CS_GRP_CALL) or i.group(CS_GRP_JUMP):
   assert i.operands[0].type==X86_OP_IMM
   target=i.operands[0].imm;assert target in known
   operand=f".L{target:x}"
  lines += [f".L{i.address:x}:",f"  {i.mnemonic} {operand}"]
(out/"comparison.S").write_text("\n".join(lines)+"\n")
env=environment();clang=str(LLVM/"bin/clang.exe");cxx=str(LLVM/"bin/clang-cl.exe")
cmds=[[clang,"-c","-march=haswell",str(out/"comparison.S"),"-o",str(out/"comparison.obj")],
[cxx,"/nologo","/c","/O2","/EHsc","/std:c++17","native/reassembly_benchmark.cpp",f"/Fo{out}/bench.obj"],
[cxx,"/nologo",str(out/"bench.obj"),str(out/"comparison.obj"),f"/Fe{out}/comparison.exe"]]
for cmd in cmds:
 print(json.dumps(cmd),flush=True);subprocess.run(cmd,env=env,check=True,timeout=120)
with (out/"results.jsonl").open("wb") as o:subprocess.run([str(out/"comparison.exe"),str(out)],stdout=o,env=env,check=True,timeout=120)
rows=[json.loads(x) for x in (out/"results.jsonl").read_text().splitlines()]
summary=dict(kind="static x64 reassembly comparison; not lifted recompilation",contract="scalar return equality on valid read-only kernel objects; normal SysV ABI; not full-state equivalence",object_bytes=(out/"comparison.obj").stat().st_size,measurements=[])
for kernel in ("loop","hash"):
 for length in (8,64):
  v=[x for x in rows if x["kernel"]==kernel and x["length"]==length]
  summary["measurements"].append(dict(kernel=kernel,length=length,median_ratio=statistics.median(x["ratio"] for x in v)))
(out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary),flush=True)
