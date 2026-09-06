"""Verify the complete recovery delta before selecting newly accepted compilation entries."""
import argparse,collections,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import SPECS,LIBC

def main():
 p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 expected={(r['module'],r['entry']):r for r in SPECS};changed=[];units=0
 with (a.before/'compilation-manifest.jsonl').open(encoding='utf-8') as old,(a.after/'compilation-manifest.jsonl').open(encoding='utf-8') as new:
  for x,y in zip(old,new,strict=True):
   units+=1
   if x==y:continue
   x=json.loads(x);y=json.loads(y);key=(x['module_sha256'],x['entry'])
   assert key==(y['module_sha256'],y['entry']) and key in expected
   spec=expected[key]
   assert len(x['issues'])==1 and not y['issues'] and x['issues'][0]['kind']=='fallthrough_at_fence'
   removed=[i for i in x['instructions'] if i not in y['instructions']]
   assert not [i for i in y['instructions'] if i not in x['instructions']]
   assert removed==([dict(rva=0x1f570,size=1,bytes='90')] if key==(LIBC,0x1f560) else [])
   added=[e for e in y['edges'] if e not in x['edges']]
   assert not [e for e in x['edges'] if e not in y['edges']]
   assert {e['kind'] for e in added}=={'unresolved_native_service_control','annotated_control_contract_requires_runtime'} and len(added)==2
   assert all(e['source']==spec['site'] for e in added)
   assert next(e['detail'] for e in added if e['kind']=='annotated_control_contract_requires_runtime')==spec['id']
   for field in x:
    if field not in ('issues','decode_status','edges','instructions','instruction_set_sha256'):assert x[field]==y[field],field
   changed.append(dict(module=key[0],start=key[1],removed_instructions=removed,added_edges=added,removed_issues=x['issues']))
 assert {(r['module'],r['start']) for r in changed}==set(expected) and units==21178
 assert (a.before/'constructor-order.json').read_bytes()==(a.after/'constructor-order.json').read_bytes()
 before=json.loads((a.before/'summary.json').read_text());after=json.loads((a.after/'summary.json').read_text())
 # Every existing unresolved target/annotation count is unchanged except the three explicitly checked fence findings.
 frontier_delta={k:after['frontier_counts'].get(k,0)-before['frontier_counts'].get(k,0) for k in set(before['frontier_counts'])|set(after['frontier_counts'])}
 frontier_delta={k:v for k,v in frontier_delta.items() if v}
 assert frontier_delta==dict(fallthrough_at_fence=-3,annotated_control_contract_requires_runtime=3,unresolved_native_service_control=3),frontier_delta
 result=dict(status='exact service-site recovery delta passed',before=str(a.before),after=str(a.after),source_db_sha256=sha(a.before/'analysis.sqlite'),target_db_sha256=sha(a.after/'analysis.sqlite'),target_manifest_sha256=sha(a.after/'compilation-manifest.jsonl'),changed=changed,frontier_delta=frontier_delta,units=units,remaining_quarantines=5,limitations='Only three conditional no-ordinary-return service sites changed. Unknown indirect and callback targets, exception paths and every old contract obligation remain.')
 write_json(a.out/'delta.json',result);write_json(a.out/'entries.json',[dict(module=r['module'],start=r['start']) for r in changed])
 print(json.dumps({k:result[k] for k in ('status','units','remaining_quarantines','frontier_delta')}))
if __name__=='__main__':main()
