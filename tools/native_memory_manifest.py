"""Verify exact startup ABI migration and deterministic repeat before publishing objects."""
import argparse,collections,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('first',type=Path);p.add_argument('repeat',type=Path);p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
identity=read(a.repeat/'identity.json');assert identity==read(a.first/'identity.json');assert identity['native_memory_provenance'];assert sha(a.source/'analysis.sqlite')==identity['source_db_sha256'];assert sha(a.source/'compilation-manifest.jsonl')==identity['source_manifest_sha256'];assert sha(a.plan/'objects.json')==identity['plan_sha256']
current={}
for line in (a.source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(hash=u['instruction_set_sha256'],ctor=u['constructor_ordinal'],issues=u['issues'])
plan=read(a.plan/'objects.json');first=read(a.first/'results.json');repeat=read(a.repeat/'results.json');assert len(plan)==len(first)==len(repeat)==386
active=[];entries=collections.Counter();roots=collections.Counter();guards=set();instructions=0;bridges=collections.Counter()
for row,one,two in zip(plan,first,repeat,strict=True):
 assert one==two and two['status']=='object_built' and two['index']==row['index'];folder=a.repeat/two['folder'];old=Path('local/compiler-spike')/row['source_batch']/row['folder'];assert sha(old/'function.obj')==row['object_sha256'] and sha(old/'input.json')==row['old_input_sha256']
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:assert sha(a.first/two['folder']/name)==sha(folder/name)
 data=read(folder/'input.json');prior=read(old/'input.json');assert data.pop('native_memory_provenance') is True and data==prior;assert sha(folder/'input.json')==row['input_sha256'];assert sha(folder/'function.obj')==two['object_sha256']
 audit=read(folder/'audit.json');assert audit['native_memory_provenance'];assert audit['compiled_roots']==data['roots']==two['compiled_roots'];assert not audit['unvisited_manifest_instructions'];assert set(audit['decoded_addresses'])=={i['address'] for i in data['instructions']};assert audit['missing_instruction_starts']==row['original_missing_instruction_starts'];assert audit['call_return_checks']==read(old/'audit.json')['call_return_checks'];bridges.update(audit['native_memory_bridges']);instructions+=len(data['instructions'])
 for u in read(folder/'units.json'):
  key=two['module'],u['entry'];assert u['instruction_set_sha256']==current[key]['hash'] and not current[key]['issues'];entries[key]+=1
 roots.update(two['compiled_roots']);guards.update(r['source'] for r in audit['call_return_checks'] if r['no_normal_return']);active.append(dict(source_batch=a.repeat.name,**{k:two[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}))
assert len(entries)==21181 and len(roots)==21282 and set(entries)==set(current) and set(entries.values())==set(roots.values())=={1};assert sum(current[k]['ctor'] is not None for k in entries)==18444 and instructions==874279 and len(guards)==4305
write_json(a.out/'active-objects.json',active)
summary=dict(status='complete startup native memory-source ABI migration repeats exactly',active_manifest_sha256=sha(a.out/'active-objects.json'),objects=386,entries=len(entries),roots=len(roots),constructors=18444,instructions=instructions,unique_nonreturn_sites=len(guards),compiler_bridge_counts=dict(bridges),object_bytes=sum(r['object_bytes'] for r in active),identity=identity,game_execution=False,limitations=['Current recovered inputs differ only by explicit native_memory_provenance=true; boundaries and conditional recovery assumptions remain unchanged.','Independent LLVM argument/control verification and complete registry/link validation are separate required steps before startup.','Object compilation and structural reachability do not establish execution coverage.'])
write_json(a.out/'evidence.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='identity'}),flush=True)
