"""Compare immutable recovery snapshots; select new entries for independent checks."""
import argparse
import collections
import json
from pathlib import Path
import sqlite3
from tools.cfg_recover_startup import sha,write_json

def connect(path):
    return sqlite3.connect(f'{(path/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);old,new=connect(a.before),connect(a.after)
    assert new.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    def entries(db):return set(db.execute('SELECT module,start FROM recovery_entry'))
    added=entries(new)-entries(old);removed=entries(old)-entries(new)
    requests=collections.Counter();new_units=[]
    for h,at in sorted(added):
        sources=new.execute('SELECT reason,parent_module,parent_entry,source FROM recovery_request WHERE module=? AND target=?',(h,at)).fetchall()
        requests.update(r[0] for r in sources)
        new_units.append(dict(module=h,entry=at,requests=sources,status=new.execute('SELECT status FROM recovery_entry WHERE module=? AND start=?',(h,at)).fetchone()[0]))
    callback_counts=collections.Counter();callback_targets=set();unknown=collections.Counter()
    for h,at,src,target,kind,detail in new.execute("SELECT module,entry,source,target,kind,detail FROM recovery_edge WHERE kind IN ('callback_contract_target_candidate','unresolved_callback_argument','callback_contract_null_argument')"):
        c=json.loads(detail)['contract'];callback_counts[c,kind]+=1
        if kind=='callback_contract_target_candidate':callback_targets.add((h,target))
        if kind=='unresolved_callback_argument':unknown[c]+=1
    old_issues=set(old.execute('SELECT * FROM recovery_issue'));new_issues=set(new.execute('SELECT * FROM recovery_issue'))
    remaining=[]
    for h,at,pc,kind,detail in sorted(new_issues):
        targets=new.execute("SELECT target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=? AND source=? AND kind NOT IN ('fallthrough','callback_argument_candidate')",(h,at,pc)).fetchall()
        remaining.append(dict(module=h,entry=at,rva=pc,kind=kind,instruction=detail,targets=targets))
    report=dict(status='static frontier comparison; P3 gate remains open',before=str(a.before),after=str(a.after),
        before_db_sha256=sha(a.before/'analysis.sqlite'),after_db_sha256=sha(a.after/'analysis.sqlite'),
        added_entries=new_units,removed_entries=sorted(removed),new_entry_request_kinds=dict(requests),
        callback_counts=[dict(contract=c,kind=k,count=n) for (c,k),n in sorted(callback_counts.items())],
        unique_callback_targets=len(callback_targets),unresolved_callback_arguments=dict(unknown),
        removed_issue_count=len(old_issues-new_issues),added_issue_count=len(new_issues-old_issues),remaining_issues=remaining,
        before_summary=json.loads((a.before/'summary.json').read_text()),after_summary=json.loads((a.after/'summary.json').read_text()),
        limitation='Static records and entry requests only. Candidate callback invocation, binding and mutation remain unvalidated. New worklist entries can expose more unresolved control; no native execution occurred.')
    write_json(a.out/'delta.json',report)
    selection={(h,at):'new_callback_closure_entry' for h,at in added}
    selection.update({(r['module'],r['entry']):'remaining_boundary_dispute' for r in remaining})
    write_json(a.out/'selection.json',[dict(module=h,start=at,reason=reason) for (h,at),reason in sorted(selection.items())])
    write_json(a.out/'new-entries.json',[dict(module=h,start=at) for h,at in sorted(added)])
    print(json.dumps(dict(added=len(added),removed=len(removed),new_entry_request_kinds=dict(requests),unique_callback_targets=len(callback_targets),callback_counts=report['callback_counts'],removed_issues=report['removed_issue_count'],added_issues=report['added_issue_count'],remaining_issues=len(remaining))),flush=True)

if __name__=='__main__':main()
