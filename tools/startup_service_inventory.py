"""Record exact termination disputes and reference identities without executing game code."""
import argparse,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json

LIBC='4378b47f46f1d856824a6f971db1a0c3f41833b77f49d2fba9538f667a139166'
MAIN='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9'
SPECS=[
 dict(id='libc-abort-debug-site',module=LIBC,entry=0x1f560,site=0x1f56b,target=0xe0,nid='OMDRKKAZ8I4',
      context={'rdi':0xa002000b,'rsi':0},context_instructions=[0x1f564,0x1f569],
      contract='Conditional absence of ordinary return at this exact abort-wrapper service call, under the existing libc-abort ABI contract and its signal/exception implementation obligations. This is not a generic debug-service noreturn contract.',
      obligations=['native abort and debug-exception binding','signal/exception disposition and possible nonlocal handler transfer','unexpected service return must be reported, never continued into the trailing NOP or adjacent data'],
      url='https://pubs.opengroup.org/onlinepubs/9699919799/functions/abort.html'),
 dict(id='libc-exit-kernel-site',module=LIBC,entry=0x5ff10,site=0x5ff5d,target=0x5a0,nid='6Z83sYWFlA8',context={},context_instructions=[],
      contract='Conditional no ordinary return for exact libkernel _exit import. Earlier libc exit callbacks remain recovered and unresolved.',
      obligations=['native process termination and status','process resource teardown and all-thread termination','no extra atexit, cancellation cleanup or thread-data destructor invocation by _exit','unexpected service return must be reported'],
      url='https://pubs.opengroup.org/onlinepubs/9799919799/functions/_exit.html'),
 dict(id='main-pthread-exit-site',module=MAIN,entry=0x207f990,site=0x207f99b,target=0x2bc0d38,nid='3kg7rT0NQIs',context={},context_instructions=[],
      contract='Conditional no ordinary return for exact scePthreadExit import aligned with the public pthread_exit contract. Callback targets and implementation remain unresolved.',
      obligations=['native thread exit value and join delivery','LIFO cancellation cleanup through validated native callback dispatch','thread-specific destructors and repeated destructor passes','last-thread process exit','unexpected service return must be reported'],
      url='https://pubs.opengroup.org/onlinepubs/009696899/functions/pthread_exit.html')]

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False)
 db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 cases=[]
 selected=set(db.execute('SELECT DISTINCT module,entry FROM recovery_issue'))
 assert selected=={(LIBC,x) for x in (0x1f560,0x5ff10,0x60510,0x60560,0x606f0)}|{(MAIN,x) for x in (0x207f990,0x210b0e0,0x210b940)}
 selected|={(LIBC,0x60750),(MAIN,0x210ad70),(LIBC,0x12f00)}
 for h,entry in sorted(selected):
  rows=[dict(rva=rva,size=size,bytes=raw,mnemonic=mn,operands=ops) for rva,size,raw,mn,ops in db.execute('SELECT i.rva,i.size,i.bytes,i.mnemonic,i.operands FROM recovery_owner o CROSS JOIN recovery_instruction i ON o.module=i.module AND o.rva=i.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,entry))]
  issues=[dict(rva=rva,kind=kind,detail=detail) for rva,kind,detail in db.execute('SELECT rva,kind,detail FROM recovery_issue WHERE module=? AND entry=?',(h,entry))]
  edges=[dict(source=src,target_module=other,target=dst,kind=kind,detail=detail) for src,other,dst,kind,detail in db.execute("SELECT source,target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=? AND kind NOT IN ('callback_argument_candidate','abi_register_preservation_unvalidated') ORDER BY source,kind,target",(h,entry))]
  cases.append(dict(module=h,entry=entry,instructions=rows,issues=issues,edges=edges))
 contracts=[]
 for spec in SPECS:
  row=dict(spec,import_key=[spec['nid'],'libkernel','libkernel'])
  case=next(c for c in cases if (c['module'],c['entry'])==(row['module'],row['entry']))
  imp=[json.loads(e['detail']) for e in case['edges'] if e['source']==row['site'] and e['kind']=='import_contract_unvalidated' and e['target']==row['target']]
  assert len(imp)==1 and [imp[0][k] for k in ('nid','library','module')]==row['import_key']
  row['instructions']=[[i['rva'],i['size'],i['bytes']] for i in case['instructions']]
  row['import']=imp[0]
  contracts.append(row)
 refs=['tools/cfg_import_contracts.json','external/shadPS4/src/core/aerolib/aerolib.inl','external/shadPS4/src/core/libraries/kernel/process.cpp','external/shadPS4/src/core/libraries/kernel/threads/exception.cpp','external/shadPS4/src/core/libraries/kernel/threads/pthread.cpp']
 data=dict(schema=1,status='service-site candidates require independent Ghidra check',source_db_sha256=sha(a.source/'analysis.sqlite'),source_manifest_sha256=sha(a.source/'compilation-manifest.jsonl'),references={p:sha(p) for p in refs},contracts=contracts,cases=cases,
  limitations='Public API contracts and pinned reference code corroborate identity; they are not PS4 observations or native runtime implementations. Unknown virtual calls, handlers, cleanup, restored contexts and mutable state remain open. No game CPU execution.')
 write_json(a.out/'inventory.json',data)
 write_json(a.out/'selection.json',[dict(module=h,start=e,reason='termination_or_nonlocal_boundary_dispute') for h,e in sorted(selected)])
 print(json.dumps(dict(cases=len(cases),conditional_service_candidates=len(contracts),quarantines=sum(bool(c['issues']) for c in cases))))
if __name__=='__main__':main()
