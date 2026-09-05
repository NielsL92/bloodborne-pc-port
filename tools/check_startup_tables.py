"""Check encoded bounds and signed-relative bytes against independent Ghidra tables."""
import hashlib,json,sqlite3,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_REG_RIP
from tools.cfg_recover_startup import canonical_register,sha,write_json
from tools.formats import ElfImage
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
source=Path('local/cfg/ghidra-startup-tables-v1');ghidra=json.loads((source/'ghidra.json').read_text());identity=json.loads((source/'input.json').read_text())
db=sqlite3.connect('file:local/cfg/startup-recovery-v3/analysis.sqlite?mode=ro',uri=True)
h=identity['module_sha256'];path=db.execute('SELECT path FROM module WHERE hash=?',(h,)).fetchone()[0];assert sha(path)==h
im=ElfImage(Path(path).read_bytes());dec=Cs(CS_ARCH_X86,CS_MODE_64);dec.detail=True;entries=[]
for fn in ghidra:
 assert len(fn['tables'])==1
 table=fn['tables'][0];branch=table['branch'];prefix=list(dec.disasm(im.at_va(fn['entry'],branch+2-fn['entry']),fn['entry']))
 assert prefix[-1].address==branch
 lea,load,add,jump=prefix[-4:]
 assert (lea.mnemonic,load.mnemonic,add.mnemonic,jump.mnemonic)==('lea','movsxd','add','jmp')
 assert lea.operands[1].type==X86_OP_MEM and lea.operands[1].mem.base==X86_REG_RIP
 table_rva=lea.address+lea.size+lea.operands[1].mem.disp
 assert load.operands[1].mem.base==lea.operands[0].reg and load.operands[1].mem.scale==4 and load.operands[1].mem.disp==0
 assert add.operands[0].reg==load.operands[0].reg==jump.operands[0].reg and add.operands[1].reg==lea.operands[0].reg
 index=canonical_register(load.reg_name(load.operands[1].mem.index))
 guards=[(n,i) for n,i in enumerate(prefix[:-4]) if i.mnemonic=='cmp' and i.operands[1].type==X86_OP_IMM and canonical_register(i.reg_name(i.operands[0].reg))==index]
 assert len(guards)==1
 pos,cmp=guards[0];guard=prefix[pos+1];assert guard.mnemonic=='ja' and guard.operands[0].type==X86_OP_IMM
 count=cmp.operands[1].imm+1;assert count==13
 for i in prefix[pos+2:-3]:assert index not in [canonical_register(i.reg_name(r)) for r in i.regs_access()[1]],i
 raw=im.at_va(table_rva,4*count);targets=[table_rva+v for v in struct.unpack('<'+str(count)+'i',raw)]
 assert targets==table['targets']
 assert not db.execute('SELECT 1 FROM relocation WHERE module=? AND location>=? AND location<?',(h,table_rva,table_rva+len(raw))).fetchall()
 for target in set(targets):assert fn['entry']<=target<table_rva and next(dec.disasm(im.at_va(target,15),target,count=1),None)
 entries.append(dict(module_sha256=h,entry=fn['entry'],branch=branch,table_rva=table_rva,count=count,targets=targets,default=guard.operands[0].imm,
   table_sha256=hashlib.sha256(raw).hexdigest(),guard_rva=cmp.address,guard_bytes=im.at_va(cmp.address,branch+2-cmp.address).hex(),
   evidence='Independent Ghidra decompiler destinations equal signed table offsets; CMP/JA dominance and unchanged index checked; no runtime target or table mutation validation.'))
report=dict(status='independent static table comparison passed',ghidra_sha256=sha(source/'ghidra.json'),entries=entries,unique_edges=sum(len(set(e['targets'])) for e in entries),execution_coverage=False)
write_json(out/'tables.json',report);print(json.dumps(report),flush=True)
