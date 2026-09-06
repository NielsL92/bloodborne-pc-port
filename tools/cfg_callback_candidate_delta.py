"""Select new callback provenance and closure bodies for independent inspection."""
import argparse,collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def connect(p):return sqlite3.connect((p/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
old,new=connect(a.before),connect(a.after)
keys=lambda db:set(db.execute('select module,start from recovery_entry'))
added=keys(new)-keys(old);assert not keys(old)-keys(new)
prior={(h,source,target) for h,source,target in old.execute("select module,source,target from recovery_edge where kind='callback_contract_target_candidate'")}
records=[];selection={(h,at):'new_callback_dependency_body' for h,at in added};new_constants=[];relocations=[]
for h,entry,source,target_module,target,kind,detail in new.execute("select * from recovery_edge where kind in ('callback_contract_target_candidate','callback_relocation_binding_unvalidated','callback_relocation_target_candidate') order by module,entry,source,kind"):
 if kind=='callback_contract_target_candidate' and (h,source,target) in prior:continue
 data=json.loads(detail);record=dict(module=h,entry=entry,source=source,target_module=target_module,target=target,kind=kind,detail=data);records.append(record);selection[h,entry]='new_callback_provenance_source'
 if kind=='callback_contract_target_candidate':new_constants.append(record)
 elif kind=='callback_relocation_binding_unvalidated':relocations.append(record)
new_issues=list(new.execute('select module,entry,rva,kind,detail from recovery_issue order by module,entry,rva'))
for h,entry,*_ in new_issues:selection.setdefault((h,entry),'remaining_boundary_dispute')
write_json(a.out/'records.json',records);write_json(a.out/'selection.json',[dict(module=h,start=at,reason=reason) for (h,at),reason in sorted(selection.items())]);write_json(a.out/'new-entries.json',[dict(module=h,start=at) for h,at in sorted(added)])
summary=dict(status='callback candidate closure delta; runtime targets remain unknown',before=str(a.before),after=str(a.after),before_db_sha256=sha(a.before/'analysis.sqlite'),after_db_sha256=sha(a.after/'analysis.sqlite'),new_entries=len(added),new_constant_argument_records=len(new_constants),relocated_binding_records=len(relocations),initial_relocated_targets=sorted({(c['module'],c['target']) for r in relocations for c in r['detail']['candidates']}),empty_relocation_bindings=sum(not r['detail']['candidates'] for r in relocations),selected_windows=len(selection),remaining_issues=len(new_issues),remaining_unknown_callback_records=new.execute("select count(*) from recovery_edge where kind='unresolved_callback_argument'").fetchone()[0],new_entry_status=dict(collections.Counter(new.execute('select status from recovery_entry where module=? and start=?',(h,at)).fetchone()[0] for h,at in added)),limitations='Initial relocation candidates are separate from unknown runtime arguments. SysV normal-return register preservation is conditional; native ABI and callbacks remain unvalidated. No game execution.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
