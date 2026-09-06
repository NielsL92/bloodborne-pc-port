"""Find exact constructor cache/factory/virtual-call instruction patterns."""
import argparse,collections,hashlib,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG,X86_REG_RIP,X86_REG_RAX,X86_REG_RBX,X86_REG_RDI,X86_REG_RSI,X86_REG_RSP,X86_REG_EDX
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);main=c.execute("select hash from module where name='eboot.bin'").fetchone()[0];constructors={r[0] for r in c.execute('select target from initializer_slot where module=?',(main,))};d=Cs(CS_ARCH_X86,CS_MODE_64);d.detail=True
calls=[(e,site) for e,site in c.execute("select entry,source from recovery_edge where module=? and kind='unresolved_indirect_call' and detail='qword ptr [rax + 0x20]' order by entry,source",(main,)) if e in constructors];cache={};matched=[];other=[]

def reg(op,value):return op.type==X86_OP_REG and op.reg==value
def mem(op,base,disp=0):return op.type==X86_OP_MEM and op.size==8 and op.mem.base==base and op.mem.disp==disp and not op.mem.index and not op.mem.segment
for entry,site in calls:
 if entry not in cache:
  cache[entry]=list(c.execute('select i.rva,i.size,i.bytes from recovery_owner o cross join recovery_instruction i on i.module=o.module and i.rva=o.rva where o.module=? and o.entry=? order by i.rva',(main,entry)))
 rows=cache[entry];position=next(n for n,r in enumerate(rows) if r[0]==site);rows=rows[max(0,position-11):position+1]
 ins=[next(d.disasm(bytes.fromhex(b),pc,count=1)) for pc,size,b in rows];ok=len(ins)==12 and [i.mnemonic for i in ins]==['lea','mov','test','jne','call','mov','mov','mov','lea','xor','mov','call']
 if ok:
  lea,load,test,jump,call,moveret,store,tableload,resultarg,zero,objectarg,dispatch=ins
  cache_reg=lea.operands[0].reg;object_reg=load.operands[0].reg;table_reg=tableload.operands[0].reg
  ok=(lea.operands[0].type==X86_OP_REG and lea.operands[0].size==8 and lea.operands[1].type==X86_OP_MEM and lea.operands[1].mem.base==X86_REG_RIP and not lea.operands[1].mem.index
      and load.operands[0].type==X86_OP_REG and load.operands[0].size==8 and mem(load.operands[1],cache_reg)
      and reg(test.operands[0],object_reg) and reg(test.operands[1],object_reg)
      and jump.operands[0].type==X86_OP_IMM and jump.operands[0].imm==tableload.address
      and call.operands[0].type==X86_OP_IMM and call.operands[0].imm==0x2ba2b10
      and reg(moveret.operands[0],object_reg) and reg(moveret.operands[1],X86_REG_RAX)
      and mem(store.operands[0],cache_reg) and reg(store.operands[1],object_reg)
      and mem(tableload.operands[1],object_reg) and table_reg==X86_REG_RAX
      and reg(resultarg.operands[0],X86_REG_RDI) and resultarg.operands[1].type==X86_OP_MEM and resultarg.operands[1].mem.base==X86_REG_RSP and not resultarg.operands[1].mem.index
      and reg(zero.operands[0],X86_REG_EDX) and reg(zero.operands[1],X86_REG_EDX)
      and reg(objectarg.operands[0],X86_REG_RSI) and reg(objectarg.operands[1],object_reg)
      and mem(dispatch.operands[0],table_reg,0x20)
      and all(x.address+x.size==y.address for x,y in zip(ins,ins[1:])))
 if not ok:other.append(dict(module=main,entry=entry,site=site));continue
 slot=lea.address+lea.size+lea.operands[1].mem.disp
 matched.append(dict(module=main,entry=entry,site=site,start=lea.address,end=dispatch.address+dispatch.size,cache_slot=slot,factory=0x2ba2b10,offset=0x20,registers=dict(cache=lea.reg_name(cache_reg),object=lea.reg_name(object_reg),table=lea.reg_name(table_reg)),instructions=[dict(pc=pc,size=size,bytes=b) for pc,size,b in rows],instruction_bytes_sha256=hashlib.sha256(b''.join(bytes.fromhex(b) for pc,size,b in rows)).hexdigest(),condition='Only a cache value produced by the checked factory and retaining the constructed initial table. Mutation, interposition, failed initialization and native ABI remain unknown.'))
write_json(a.out/'matches.json',matched);write_json(a.out/'other-sites.json',other)
summary=dict(status='exact constructor dispatch shape inventory; independent cohort check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),constructor_call_sites=len(calls),matched=len(matched),other_shapes=len(other),cache_slots=[dict(slot=slot,count=n) for slot,n in sorted(collections.Counter(r['cache_slot'] for r in matched).items())],matched_instructions=sum(len(r['instructions']) for r in matched),limitations='Exact finite instruction shape only. This does not prove cache/table immutability, successful construction, execution coverage or a unique runtime target. Nonmatching shapes are retained.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
