"""Bounded backward register slices over recovered normal-flow predecessors."""
import argparse,collections,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG,X86_REG_RIP
from tools.cfg_recover_startup import canonical_register,sha,write_json
SAVED={'rbx','rbp','r12','r13','r14','r15'}

def slice_register(instructions,predecessors,roots,pc,register,budget=2048):
    active=set();visited=set();evidence=set();assumptions=set();failures=set()
    def before(pc,reg):
        key=(pc,reg)
        if key in active:failures.add(('cycle',pc,reg));return set()
        if len(visited)>=budget:failures.add(('budget',pc,reg));return set()
        visited.add(key)
        if pc in roots:failures.add(('entry-register',pc,reg));return set()
        parents=predecessors.get(pc,[])
        if not parents:failures.add(('missing-predecessor',pc,reg));return set()
        active.add(key);result=set()
        for parent in parents:result.update(after(parent,reg))
        active.remove(key);return result
    def after(pc,reg):
        i=instructions[pc];evidence.add(pc)
        if i.group(CS_GRP_CALL):
            if reg not in SAVED:failures.add(('volatile-call-result',pc,reg));return set()
            assumptions.add(pc);return before(pc,reg)
        written={canonical_register(i.reg_name(r)) for r in i.regs_access()[1]}
        if reg not in written:return before(pc,reg)
        if len(i.operands)>=2:
            dst,src=i.operands[:2]
            if dst.type==X86_OP_REG and canonical_register(i.reg_name(dst.reg))==reg:
                if dst.size not in (4,8):failures.add(('partial-write',pc,reg));return set()
                if i.mnemonic in ('mov','movabs'):
                    if src.type==X86_OP_IMM:return {('absolute',src.imm&((1<<(dst.size*8))-1))}
                    if src.type==X86_OP_REG and dst.size==src.size==8:return before(pc,canonical_register(i.reg_name(src.reg)))
                if i.mnemonic in ('xor','sub') and src.type==X86_OP_REG and src.reg==dst.reg:return {('absolute',0)}
                if i.mnemonic=='lea' and dst.size==8 and src.type==X86_OP_MEM and src.mem.base==X86_REG_RIP and not src.mem.index:return {('module-rva',pc+i.size+src.mem.disp)}
        failures.add(('unknown-write',pc,reg));return set()
    targets=before(pc,register)
    return dict(complete=not failures,targets=[dict(kind=k,value=v) for k,v in sorted(targets)],failures=[dict(reason=r,pc=p,register=g) for r,p,g in sorted(failures)],instructions=sorted(evidence),conditional_normal_sysv_returns=sorted(assumptions),states=len(visited))

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
 relocated={(h,e,s) for h,e,s in c.execute("select module,entry,source from recovery_edge where kind='callback_relocation_target_candidate'")};records=[];selection={}
 for h,entry,site,detail in c.execute("select module,entry,source,detail from recovery_edge where kind='unresolved_callback_argument' order by module,entry,source"):
  if (h,entry,site) in relocated:continue
  contract=json.loads(detail);raw=list(c.execute('select i.rva,i.size,i.bytes from recovery_owner o cross join recovery_instruction i on i.module=o.module and i.rva=o.rva where o.module=? and o.entry=? order by i.rva',(h,entry)))
  ins={pc:next(decoder.disasm(bytes.fromhex(b),pc,count=1)) for pc,size,b in raw};pred=collections.defaultdict(set)
  for src,target in c.execute("select source,target from recovery_edge where module=? and entry=? and target_module=? and kind in ('fallthrough','direct_jump','validated_jump_table','independently_recovered_jump_table')",(h,entry,h)):
   if src in ins and target in ins:pred[target].add(src)
  roots={entry}|{r[0] for r in c.execute('select landing_pad from exception_call_site where module=? and range_start=? and landing_pad is not null',(h,entry))}
  result=slice_register(ins,pred,roots,site,contract['register']);result.update(module=h,entry=entry,site=site,contract=contract,roots=sorted(roots),source_instructions=[dict(pc=pc,size=size,bytes=b) for pc,size,b in raw],predecessors={str(pc):sorted(v) for pc,v in sorted(pred.items())})
  records.append(result);selection[h,entry]='remaining_callback_argument_slice'
 write_json(a.out/'slices.json',records);write_json(a.out/'selection.json',[dict(module=h,start=entry,reason=reason) for (h,entry),reason in sorted(selection.items())])
 summary=dict(status='bounded backward callback slices; independent check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),records=len(records),complete=sum(r['complete'] for r in records),results=[dict(module=r['module'],entry=r['entry'],site=r['site'],complete=r['complete'],targets=r['targets'],failures=r['failures']) for r in records],limitations='Normal recovered CFG and explicit metadata roots only. Missing predecessors, cycles, unsupported writes and volatile call results stay unknown. Conditional SysV return preservation is retained. No game execution.')
 write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
