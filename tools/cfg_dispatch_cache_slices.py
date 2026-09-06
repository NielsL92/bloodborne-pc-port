"""Slice earlier cache-register definitions at constructor dispatch sites."""
import argparse,collections,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG,X86_REG_RAX,X86_REG_RDI,X86_REG_RSI,X86_REG_RSP,X86_REG_EDX
from tools.cfg_callback_slices import slice_register,SAVED
from tools.cfg_recover_startup import sha,write_json

def reg(op,value):return op.type==X86_OP_REG and op.reg==value

def mem(op,base,disp=0):return op.type==X86_OP_MEM and op.size==8 and op.mem.base==base and op.mem.disp==disp and not op.mem.index and not op.mem.segment

def tail(ins):
 if len(ins) not in (11,12) or any(x.address+x.size!=y.address for x,y in zip(ins,ins[1:])):return None
 normal=list(ins);offset=0
 if len(ins)==12:
  add=normal.pop(5)
  if add.mnemonic!='add' or add.operands[0].type!=X86_OP_REG or add.operands[0].size!=8 or add.operands[1].type!=X86_OP_IMM or add.operands[1].imm!=0x458:return None
  offset=0x458
 if [i.mnemonic for i in normal]!=['mov','test','jne','call','mov','mov','mov','lea','xor','mov','call']:return None
 load,test,jump,factory,result,store,table,arg,zero,objarg,dispatch=normal
 if load.operands[0].type!=X86_OP_REG or load.operands[0].size!=8 or load.operands[1].type!=X86_OP_MEM:return None
 obj,cache=load.operands[0].reg,load.operands[1].mem.base
 if load.reg_name(cache) not in SAVED or load.reg_name(obj) not in SAVED or obj==cache or not mem(load.operands[1],cache):return None
 if offset and not reg(add.operands[0],obj):return None
 if not (reg(test.operands[0],obj) and reg(test.operands[1],obj) and jump.operands[0].type==X86_OP_IMM and jump.operands[0].imm==table.address):return None
 expected=0x207bbf0 if offset else 0x2ba2b10
 if factory.operands[0].type!=X86_OP_IMM or factory.operands[0].imm!=expected:return None
 if not (reg(result.operands[0],obj) and reg(result.operands[1],X86_REG_RAX) and mem(store.operands[0],cache) and reg(store.operands[1],obj) and reg(table.operands[0],X86_REG_RAX) and mem(table.operands[1],obj)):return None
 if not (reg(arg.operands[0],X86_REG_RDI) and arg.operands[1].type==X86_OP_MEM and arg.operands[1].mem.base==X86_REG_RSP and not arg.operands[1].mem.index and not arg.operands[1].mem.segment):return None
 if not (reg(zero.operands[0],X86_REG_EDX) and reg(zero.operands[1],X86_REG_EDX) and reg(objarg.operands[0],X86_REG_RSI) and reg(objarg.operands[1],obj) and mem(dispatch.operands[0],X86_REG_RAX,0x20)):return None
 return dict(cache_register=load.reg_name(cache),object_register=load.reg_name(obj),factory=expected,object_offset=offset,table_slot_offset=0x20,load_site=load.address,dispatch_site=dispatch.address)

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);d=Cs(CS_ARCH_X86,CS_MODE_64);d.detail=True
 selected={(h,e,s) for h,e,s in c.execute("select module,entry,source from recovery_edge where kind='initial_object_dispatch_target_candidate'")};constructors={(h,t) for h,t in c.execute('select module,target from initializer_slot')};records=[];other=[];selection={};cache={}
 for h,entry,site in c.execute("select module,entry,source from recovery_edge where kind='unresolved_indirect_call' and detail='qword ptr [rax + 0x20]' order by module,entry,source"):
  if (h,entry) not in constructors or (h,entry,site) in selected:continue
  if (h,entry) not in cache:
   raw=list(c.execute('select i.rva,i.size,i.bytes from recovery_owner o cross join recovery_instruction i on i.module=o.module and i.rva=o.rva where o.module=? and o.entry=? order by i.rva',(h,entry)));ins={pc:next(d.disasm(bytes.fromhex(b),pc,count=1)) for pc,size,b in raw};pred=collections.defaultdict(set)
   for src,dst in c.execute("select source,target from recovery_edge where module=? and entry=? and target_module=? and kind in ('fallthrough','direct_jump','validated_jump_table','independently_recovered_jump_table')",(h,entry,h)):
    if src in ins and dst in ins:pred[dst].add(src)
   roots={entry}|{r[0] for r in c.execute('select landing_pad from exception_call_site where module=? and range_start=? and landing_pad is not null',(h,entry))};cache[h,entry]=(raw,ins,pred,roots)
  raw,ins,pred,roots=cache[h,entry];addresses=list(ins);pos=addresses.index(site);form=None
  for width in (11,12):
   tail_pcs=addresses[max(0,pos-width+1):pos+1];form=tail([ins[pc] for pc in tail_pcs])
   if form:break
  if not form:other.append(dict(module=h,entry=entry,site=site));continue
  result=slice_register(ins,pred,roots,form['load_site'],form['cache_register'])
  result.update(module=h,entry=entry,site=form['load_site'],contract=dict(register=form['cache_register']),tail=form,tail_pcs=tail_pcs,roots=sorted(roots),source_instructions=[dict(pc=pc,size=size,bytes=b) for pc,size,b in raw])
  records.append(result);selection[h,entry]='earlier_constructor_cache_register_slice';print(json.dumps(dict(entry=hex(entry),site=hex(site),complete=result['complete'],states=result['states'])),flush=True)
 write_json(a.out/'slices.json',records);write_json(a.out/'other-sites.json',other);write_json(a.out/'selection.json',[dict(module=h,start=e,reason=r) for (h,e),r in sorted(selection.items())])
 summary=dict(status='constructor cache register slices; independent check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),records=len(records),complete=sum(r['complete'] for r in records),distinct_entries=len(selection),other=len(other),results=[dict(entry=r['entry'],dispatch_site=r['tail']['dispatch_site'],complete=r['complete'],targets=r['targets'],failures=r['failures'],sysv_calls=len(r['conditional_normal_sysv_returns'])) for r in records],limitations='Earlier cache address only. Object/cache/table contents and native factory execution remain unknown; cycles, missing/metadata entries and unsupported writes remain failures.')
 write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
