"""Record each disputed startup fence and its explicit callee candidates."""
import argparse,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False);db=sqlite3.connect(f'{(a.source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
rows=[];selection={}
for h,entry,at,kind,detail in db.execute('SELECT * FROM recovery_issue ORDER BY module,entry,rva'):
 edges=[dict(target_module=m,target=t,kind=k,detail=json.loads(d) if d.startswith('{') else d) for m,t,k,d in db.execute("SELECT target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=? AND source=? AND kind!='fallthrough' ORDER BY kind,target",(h,entry,at))]
 instructions=[dict(rva=pc,bytes=raw,mnemonic=mn,operands=ops) for pc,raw,mn,ops in db.execute('SELECT i.rva,i.bytes,i.mnemonic,i.operands FROM recovery_owner o CROSS JOIN recovery_instruction i ON o.module=i.module AND o.rva=i.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,entry))]
 rows.append(dict(module=h,entry=entry,site=at,kind=kind,detail=detail,edges=edges,instructions=instructions))
 for e in edges:
  if e['kind'] in ('direct_call','bundled_export_candidate'):
   selection.setdefault((e['target_module'],e['target']),[]).append(dict(module=h,entry=entry,site=at))
write_json(a.out/'inventory.json',dict(source_db_sha256=sha(a.source/'analysis.sqlite'),findings=rows,execution='none; disputed function boundaries remain quarantined'))
write_json(a.out/'selection.json',[dict(module=h,start=pc,reason='callee at recorded startup fence',callers=callers) for (h,pc),callers in sorted(selection.items())])
print(json.dumps(dict(findings=len(rows),callee_candidates=len(selection))),flush=True)
