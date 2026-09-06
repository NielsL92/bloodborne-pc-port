"""Verify two conditional stored Lua panic targets addition without dropping unknown control."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import MAIN
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
old=(a.before/'compilation-manifest.jsonl').open(encoding='utf-8');new=(a.after/'compilation-manifest.jsonl').open(encoding='utf-8');x=next(old,None);y=next(new,None);unchanged=0;added=[];changed=[]
while x is not None or y is not None:
 assert y is not None
 if x==y:unchanged+=1;x=next(old,None);y=next(new,None);continue
 ny=json.loads(y);nk=(ny['module_sha256'],ny['entry'])
 if nk in {(MAIN,0x2100e00),(MAIN,0x21155e0)}:
  assert not ny['issues'] and len(ny['instructions'])==(8 if nk[1]==0x2100e00 else 2) and ny['instructions'][-1]['bytes']=='c3';added.append(ny);y=next(new,None);continue
 assert x is not None;ox=json.loads(x);ok=(ox['module_sha256'],ox['entry']);assert ok==nk==(MAIN,0x210ad70)
 assert {k:v for k,v in ox.items() if k!='edges'}=={k:v for k,v in ny.items() if k!='edges'}
 edges=[e for e in ny['edges'] if e not in ox['edges']];assert len(edges)==4 and {e['kind'] for e in edges}=={'lua_panic_binding_unvalidated','stored_lua_panic_target_candidate'}
 assert not [e for e in ox['edges'] if e not in ny['edges']]
 assert all(e['source']==0x210ad84 for e in edges)
 assert any(e['source']==0x210ad84 and e['kind']=='unresolved_indirect_call' for e in ny['edges'])
 changed.append(dict(module=MAIN,entry=0x210ad70,added_edges=edges));x=next(old,None);y=next(new,None)
old.close();new.close();assert len(added)==2 and len(changed)==1 and unchanged==21178
before=json.loads((a.before/'summary.json').read_text(encoding='utf-8'));after=json.loads((a.after/'summary.json').read_text(encoding='utf-8'))
fd={k:after['frontier_counts'].get(k,0)-before['frontier_counts'].get(k,0) for k in set(before['frontier_counts'])|set(after['frontier_counts'])};fd={k:v for k,v in fd.items() if v}
assert fd==dict(logical_return_requires_dispatch=2,lua_panic_binding_unvalidated=2,stored_lua_panic_target_candidate=2),fd
assert (a.before/'constructor-order.json').read_bytes()==(a.after/'constructor-order.json').read_bytes()
assert after['counts']['recovery_entry']==21181 and after['counts']['recovery_instruction']==874279 and after['counts']['recovery_issue']==5
r=dict(status='exact two-body Lua panic recovery delta passed',before=str(a.before),after=str(a.after),source_db_sha256=sha(a.before/'analysis.sqlite'),target_db_sha256=sha(a.after/'analysis.sqlite'),target_manifest_sha256=sha(a.after/'compilation-manifest.jsonl'),unchanged_entries=unchanged,changed=changed,added=added,frontier_delta=fd,limitations='Initial target dependency only; all prior unknown, service and exception records are retained. Five quarantines remain.')
write_json(a.out/'delta.json',r);write_json(a.out/'entries.json',[dict(module=x['module_sha256'],start=x['entry']) for x in added]);print(json.dumps(dict(status=r['status'],unchanged_entries=unchanged,new_entries=2,frontier_delta=fd)))
