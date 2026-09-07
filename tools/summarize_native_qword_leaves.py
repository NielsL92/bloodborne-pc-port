"""Verify two observed qword accessors and reproducible combined startup manifests."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v22-qword48-leaf/summary.json'),read(base/'startup-v23-qword48-leaf-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v22-qword48-leaf').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v23-qword48-leaf-repeat'/path.name);artifacts[path.name]=sha(path)
leafs=[]
for tag,pc in [('2375af0',0x102375af0),('2375b00',0x102375b00)]:
 first=Path('local/compiler-spike')/('native-leaf-'+tag+'-v1');repeat=Path('local/compiler-spike')/('native-leaf-'+tag+'-v2-repeat');leaf=read(repeat/'summary.json');assert leaf==read(first/'summary.json');assert leaf['positive']['cases']==3072 and leaf['negative_stops']==2 and leaf['compiled_roots']==[pc] and leaf['load_width']==8
 for name,digest in {**leaf['files'],**leaf['native_objects']}.items():assert sha(first/name)==sha(repeat/name)==digest
 leafs.append(leaf)
for name in ['input.json','audit.json','function.bc','function.obj']:assert sha(Path('local/compiler-spike/native-leaf-207f3b0-v2-repeat')/name)==sha(Path('local/compiler-spike/native-leaf-207f3b0-v3-general')/name)
assert two['compiled_roots']==21285 and two['compiled_objects']==389 and len(two['supplements'])==3
assert stable(read(base/'startup-v20-qword-leaf/summary.json'))==stable(read(base/'startup-v21-qword-leaf-repeat/summary.json'))
calls=[json.loads(s) for s in (base/'startup-v23-qword48-leaf-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==359;last=calls[-1];assert last['target']==0x102375b10 and last['rsp']==0x700000ffea8 and last['memory_operations']==2035
returned=[r for r in calls if r['target'] in [0x102375af0,0x102375b00] and r['event']=='dispatch-return'];assert {r['target'] for r in returned}=={0x102375af0,0x102375b00}
assert two['fault']['reason']==27 and two['fault']['boundary']=='unknown-compiled-target' and two['active_import'] is None;assert two['private_image_before_native_initialization']['guards']==30
constructors=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in constructors};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(90)) and [r['ordinal'] for r in completed]==list(range(89));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
records=[]
for suffix in ['recover-native-qword-leaf-v1','ghidra-native-qword-leaf-v1','compile-native-qword-leaf-v1','compile-native-qword-leaf-v2-repeat','native-byte-leaf-general-regression','native-qword-leaf-manifest-v1','startup-qword-leaf-v1','startup-qword-leaf-v2-repeat','recover-native-qword48-leaf-v1','ghidra-native-qword48-leaf-v1','compile-native-qword48-leaf-v1','compile-native-qword48-leaf-v2-repeat','native-qword48-leaf-manifest-v1','startup-qword48-leaf-v1','startup-qword48-leaf-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='two recovered qword accessors execute and startup reaches a constant-address accessor',current=two,leaf_validations=leafs,completed_constructors=completed,entered_constructor=entered[-1],leaf_returns=returned,trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Only two additional observed five-byte targets are added. Constructor ordinal 89 remains in progress.','Generalized byte/qword load fixtures and LLVM checks validate these bodies, not target discovery or execution closure.','All original bytes remain NX; 29 prior data/TLS guards and one guarded TCB envelope remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],trace_events=len(calls),completed_constructors=len(completed))),flush=True)
