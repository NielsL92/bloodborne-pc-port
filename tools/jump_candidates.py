"""Select real small closed indirect-jump/global candidates; no execution claim."""
import json,hashlib,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG,X86_REG_RIP
from tools.formats import ElfImage
raw=Path("local/update/uroot/eboot.bin").read_bytes();image=ElfImage(raw)
decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
found=[]
for fn in image.unwind_functions():
 if not 24<=fn["size"]<=8192:continue
 b=image.at_va(fn["start"],fn["size"]);ins=list(decoder.disasm(b,fn["start"]))
 if not ins:continue
 jumps=[i for i in ins if i.group(CS_GRP_JUMP)]
 if not any(i.operands[0].type!=X86_OP_IMM for i in jumps):continue
 indirect=[i for i in jumps if i.operands[0].type!=X86_OP_IMM]
 if not any(any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in i.operands) and i.address<indirect[0].address for i in ins):continue
 if not any(o.type==X86_OP_MEM and o.mem.index!=0 and o.mem.scale in (4,8) for i in ins for o in i.operands):continue
 if len(ins)<12:continue
 if not any(i.operands[0].type==X86_OP_MEM and i.operands[0].mem.index!=0 for i in indirect) and not any(i.mnemonic=="movsxd" and any(o.type==X86_OP_MEM and o.mem.index!=0 and o.mem.scale==4 for o in i.operands) for i in ins):continue
 found.append(dict(fn,sha256=hashlib.sha256(b).hexdigest(),disassembly=[f"{i.address:x}: {i.mnemonic} {i.op_str}" for i in ins]))
 if len(found)>=12:break
out=Path(sys.argv[1])
with out.open("x") as f:json.dump(dict(input_sha256=hashlib.sha256(raw).hexdigest(),candidates=found),f,indent=2)
print(json.dumps([dict(start=hex(x["start"]),size=x["size"]) for x in found]))
