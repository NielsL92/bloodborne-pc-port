"""Verify supplemental target recovery, native semantics, and the next startup stop."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v14-native-leaf/summary.json'),read(base/'startup-v15-native-leaf-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v14-native-leaf').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v15-native-leaf-repeat'/path.name);artifacts[path.name]=sha(path)
leaf=read('local/compiler-spike/native-leaf-207f3b0-v2-repeat/summary.json');assert leaf==read('local/compiler-spike/native-leaf-207f3b0-v1/summary.json');assert leaf['positive']['cases']==3072 and leaf['negative_stops']==2
extension=read('local/compiler-spike/native-leaf-manifest-v1/manifest.json');assert two['supplements']==[dict(manifest_sha256=sha(Path('local/compiler-spike/native-leaf-manifest-v1/manifest.json')),manifest=extension)];assert two['compiled_roots']==21283 and two['compiled_objects']==387
calls=[json.loads(s) for s in (base/'startup-v15-native-leaf-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==253;last=calls[-1];assert last['target']==0x102bc0cd8 and last['rsp']==0x700000ffed8 and last['memory_operations']==1208
returned=[r for r in calls if r['target']==0x10207f3b0 and r['event']=='dispatch-return'];assert len(returned)==1;assert returned[0]['pc']==0x10207f2bf and returned[0]['rsp']==0x700000ffee0 and returned[0]['memory_operations']==1207
assert two['fault']['reason']==25 and two['fault']['boundary']=='unimplemented-import' and two['active_import']['nid']=='6ULAa0fq4jA';assert two['private_image_before_native_initialization']['guards']==29
constructors=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in constructors};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(90)) and [r['ordinal'] for r in completed]==list(range(89));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
records=[]
for suffix in ['recover-native-target-v1','ghidra-native-target-v1','compile-native-leaf-v1','compile-native-leaf-v2-repeat','native-leaf-manifest-v1','startup-native-leaf-v1','startup-native-leaf-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='recovered byte leaf executes and startup reaches reader/writer lock initialization',current=two,recovery=read('local/cfg/native-target-207f3b0-v1/recovery.json'),leaf_validation=leaf,extension=extension,completed_constructors=completed,entered_constructor=entered[-1],leaf_return=returned[0],trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Only one observed four-byte target is added. Constructor ordinal 89 is still in progress.','The native return proves this one invocation under the recorded inputs, not function/discovery/execution closure.','All source bytes remain NX; 29 unresolved data/TLS guards and prior runtime uncertainty remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],trace_events=len(calls),completed_constructors=len(completed))),flush=True)
