"""Select every changed nullable callback and removed fence for independent decoding."""
import argparse,collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def connect(path):return sqlite3.connect(f'{(path/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
old,new=connect(a.before),connect(a.after);selection={};resolved=[]
for h,entry,site,detail in new.execute("SELECT module,entry,source,detail FROM recovery_edge WHERE kind='callback_contract_null_argument' ORDER BY module,entry,source"):
 previous=old.execute("SELECT detail FROM recovery_edge WHERE module=? AND entry=? AND source=? AND kind='unresolved_callback_argument'",(h,entry,site)).fetchall();assert len(previous)==1
 current=json.loads(detail);prior=json.loads(previous[0][0]);assert current['contract']==prior['contract'];assert current['provenance'] and len(current['provenance'])==1
 pc=current['provenance'][0];ins=new.execute('SELECT bytes,mnemonic,operands FROM recovery_instruction WHERE module=? AND rva=?',(h,pc)).fetchone()
 resolved.append(dict(module=h,entry=entry,site=site,previous=prior,current=current,definition=dict(rva=pc,bytes=ins[0],mnemonic=ins[1],operands=ins[2])))
 selection[h,entry]='nullable callback provenance change'
removed_issues=sorted(set(old.execute('SELECT * FROM recovery_issue'))-set(new.execute('SELECT * FROM recovery_issue')))
for h,entry,*_ in removed_issues:selection[h,entry]='resolved final call boundary'
changed=[]
for h,entry in sorted(set(new.execute('SELECT module,start FROM recovery_entry'))):
 def ins(db):return db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON o.module=i.module AND o.rva=i.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,entry)).fetchall()
 before,after=ins(old),ins(new)
 if before!=after:
  changed.append(dict(module=h,entry=entry,removed=sorted(set(before)-set(after)),added=sorted(set(after)-set(before))))
  selection[h,entry]='changed decoded instruction set'
write_json(a.out/'changes.json',dict(before_db_sha256=sha(a.before/'analysis.sqlite'),after_db_sha256=sha(a.after/'analysis.sqlite'),resolved_nullable_arguments=resolved,removed_issues=removed_issues,changed_instruction_sets=changed,limitation='Zero idioms establish nullable argument values only. Callback invocation, pointer relocation/provenance, path merges and runtime binding remain unvalidated.'))
write_json(a.out/'selection.json',[dict(module=h,start=entry,reason=reason) for (h,entry),reason in sorted(selection.items())])
print(json.dumps(dict(nullable_arguments=len(resolved),removed_issues=len(removed_issues),changed_instruction_sets=len(changed),independent_windows=len(selection))),flush=True)
