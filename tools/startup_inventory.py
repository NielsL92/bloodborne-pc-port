"""Recover the pinned executable initializer roots from exact code and relocated data.

This is a static initial-state inventory. Constructor writes and dynamically registered
callbacks still require runtime observations and strict unknown-target diagnostics.
"""
import hashlib,json,sqlite3,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
from tools.formats import ElfImage,unpack
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect(root/"local/cfg/seed-v1/analysis.sqlite")
digest,path=db.execute("SELECT hash,path FROM module WHERE name='eboot.bin'").fetchone()
raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
im=ElfImage(raw);link=im.linkage();rel={r["offset"]:r for r in link["relocations"]}
body=im.at_va(0x20,0x71)
assert hashlib.sha256(body).hexdigest()=="cfbc899269540e0049fd48c4c486f5578379f53ba329043f09db87bca7dac662"
decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
instructions={i.address:i for i in decoder.disasm(body,0x20)}
assert sum(i.size for i in instructions.values())==len(body) and instructions[0x90].mnemonic=="ret"
def rip_target(address):
 ins=instructions[address];op=next(o for o in ins.operands if o.type==X86_OP_MEM)
 assert op.mem.base==X86_REG_RIP
 return address+ins.size+op.mem.disp
def relocated_pointer(address):
 value=unpack("<Q",im.at_va(address,8))[0]
 r=rel.get(address)
 if r:
  assert r["type"]==8 and r["symbol"]==0,(address,r)
  return r["addend"],"R_X86_64_RELATIVE"
 return value,"file value"
reverse_start=rip_target(0x2a);forward_start=rip_target(0x31)
forward_guard_slot=rip_target(0x38);forward_end=rip_target(0x41)
forward_guard,guard_evidence=relocated_pointer(forward_guard_slot)
assert forward_start==forward_end==forward_guard
assert instructions[0x3f].mnemonic=="jae" and instructions[0x3f].operands[0].imm==0x74
assert instructions[0x58].mnemonic==instructions[0x82].mnemonic=="call"
indexed={r[0] for r in db.execute("SELECT start FROM unwind_range WHERE module=?",(digest,))}
roots=[];skipped=[];address=reverse_start
for ordinal in range(100000):
 target,evidence=relocated_pointer(address)
 if target==0xffffffffffffffff:
  sentinel=address;break
 if target:
  assert any(s.type in (1,0x61000010) and s.flags&1 and s.vaddr<=target<s.vaddr+s.filesz for s in im.segments),(address,target)
  roots.append(dict(ordinal=len(roots),slot=address,target=target,evidence=evidence,indexed_unwind_start=target in indexed))
 else:skipped.append(address)
 address-=8
else:raise RuntimeError("initializer sentinel not found within bound")
# Preserve a separate relocation-applied analysis view for the independent decoder.
global_end=forward_guard_slot+8
global_data=bytearray(im.at_va(sentinel,global_end-sentinel))
applied=[]
for address,r in sorted(rel.items()):
 if sentinel<=address<global_end:
  assert r["type"]==8 and r["symbol"]==0
  struct.pack_into("<Q",global_data,address-sentinel,r["addend"])
  applied.append(dict(slot=address,target=r["addend"]))
(out/"original.bin").write_bytes(body)
(out/"globals-relocated.bin").write_bytes(global_data)
imports=json.loads((root/"local/analysis/imports.json").read_text())
names={s["nid"]:s.get("resolved_name") for s in imports}
entry_calls=[]
for ins in decoder.disasm(im.at_va(im.entry,79),im.entry):
 if ins.mnemonic!="call":continue
 target=ins.operands[0].imm
 stub=next(decoder.disasm(im.at_va(target,15),target,count=1),None);symbol=None
 if stub and stub.mnemonic=="jmp" and stub.operands[0].type==X86_OP_MEM and stub.operands[0].mem.base==X86_REG_RIP:
  got=target+stub.size+stub.operands[0].mem.disp
  r=rel.get(got)
  if r and r["type"]==7:
   symbol=dict(link["symbols"][r["symbol"]]);symbol["resolved_name"]=names.get(symbol["nid"])
 entry_calls.append(dict(caller=ins.address,target=target,symbol=symbol))
summary=dict(status="startup static roots recovered; P3 compilation/exit closure gate NOT passed",
 input_sha256=digest,initializer=dict(start=0x20,size=len(body),sha256=hashlib.sha256(body).hexdigest(),indexed_unwind_start=False,instructions=len(instructions),forward_call_site=0x58,reverse_call_site=0x82),
 forward_array=dict(start=forward_start,end=forward_end,guard_slot=forward_guard_slot,guard_value=forward_guard,guard_evidence=guard_evidence,initial_entries=0),
 reverse_array=dict(first_slot=reverse_start,sentinel=sentinel,entries=len(roots),unique_targets=len({r["target"] for r in roots}),indexed_unwind_starts=sum(r["indexed_unwind_start"] for r in roots),unindexed_roots=sum(not r["indexed_unwind_start"] for r in roots),skipped_null_slots=skipped),
 analysis_globals=dict(start=sentinel,size=len(global_data),sha256=hashlib.sha256(global_data).hexdigest(),relocations=len(applied)),
 entry_calls=entry_calls,limitations="Initial relocated data only. Executed initializers may modify remaining entries or register callbacks. Roots are not necessarily full functions; no constructor code or game entry was executed/compiled in this inventory.")
for name,value in (("summary.json",summary),("roots.json",roots),("relocations.json",applied)):
 (out/name).write_bytes((json.dumps(value,indent=2)+"\n").encode())
db.close()
print(json.dumps(summary),flush=True)
