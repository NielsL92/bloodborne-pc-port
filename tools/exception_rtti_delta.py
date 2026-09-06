"""Verify a single initial RTTI target addition without dropping unknown control."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import LIBC
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
old=(a.before/'compilation-manifest.jsonl').open(encoding='utf-8');new=(a.after/'compilation-manifest.jsonl').open(encoding='utf-8');x=next(old,None);y=next(new,None);unchanged=0;added=[];changed=[]
while x is not None or y is not None:
 assert y is not None
 if x==y:unchanged+=1;x=next(old,None);y=next(new,None);continue
 ny=json.loads(y);nk=(ny['module_sha256'],ny['entry'])
 if nk==(LIBC,0x48f00):
  assert not ny['issues'] and len(ny['instructions'])==4 and ny['instructions'][-1]['bytes']=='c3';added.append(ny);y=next(new,None);continue
 assert x is not None;ox=json.loads(x);ok=(ox['module_sha256'],ox['entry']);assert ok==nk==(LIBC,0x60750)
 assert {k:v for k,v in ox.items() if k!='edges'}=={k:v for k,v in ny.items() if k!='edges'}
 edges=[e for e in ny['edges'] if e not in ox['edges']];assert len(edges)==2 and {e['kind'] for e in edges}=={'symbol_dispatch_binding_unvalidated','initial_symbol_dispatch_target_candidate'}
 assert not [e for e in ox['edges'] if e not in ny['edges']]
 assert all(e['source']==0x60811 for e in edges)
 assert any(e['source']==0x60811 and e['kind']=='unresolved_indirect_call' for e in ny['edges'])
 changed.append(dict(module=LIBC,entry=0x60750,added_edges=edges));x=next(old,None);y=next(new,None)
old.close();new.close();assert len(added)==len(changed)==1 and unchanged==21177
before=json.loads((a.before/'summary.json').read_text(encoding='utf-8'));after=json.loads((a.after/'summary.json').read_text(encoding='utf-8'))
fd={k:after['frontier_counts'].get(k,0)-before['frontier_counts'].get(k,0) for k in set(before['frontier_counts'])|set(after['frontier_counts'])};fd={k:v for k,v in fd.items() if v}
assert fd==dict(logical_return_requires_dispatch=1,symbol_dispatch_binding_unvalidated=1,initial_symbol_dispatch_target_candidate=1),fd
assert (a.before/'constructor-order.json').read_bytes()==(a.after/'constructor-order.json').read_bytes()
assert after['counts']['recovery_entry']==21179 and after['counts']['recovery_instruction']==874269 and after['counts']['recovery_issue']==5
r=dict(status='exact one-body RTTI recovery delta passed',before=str(a.before),after=str(a.after),source_db_sha256=sha(a.before/'analysis.sqlite'),target_db_sha256=sha(a.after/'analysis.sqlite'),target_manifest_sha256=sha(a.after/'compilation-manifest.jsonl'),unchanged_entries=unchanged,changed=changed,added=added,frontier_delta=fd,limitations='Initial target dependency only; all prior unknown, service and exception records are retained. Five quarantines remain.')
write_json(a.out/'delta.json',r);write_json(a.out/'entries.json',[dict(module=LIBC,start=0x48f00)]);print(json.dumps(dict(status=r['status'],unchanged_entries=unchanged,new_entries=1,frontier_delta=fd)))
