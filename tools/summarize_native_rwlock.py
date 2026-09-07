"""Verify native reader/writer ownership and the first FS-based startup stop."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v16-rwlock/summary.json'),read(base/'startup-v17-rwlock-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v16-rwlock').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v17-rwlock-repeat'/path.name);artifacts[path.name]=sha(path)
authored=read('local/runtime/rwlock-v2-repeat/summary.json');assert authored==read('local/runtime/rwlock-v1/summary.json');assert authored['positive']['aot_service_calls']==68630 and authored['negative_stops']==8
contract=read('local/runtime/rwlock-contract-v1/contract.json');assert sha(Path('local/runtime/rwlock-contract-v1/contract.json'))==two['native_service_contract_sha256'] and two['native_service_bindings']==contract['bindings'];assert len(contract['bindings'])==41
calls=[json.loads(s) for s in (base/'startup-v17-rwlock-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==298;last=calls[-1];assert last['memory_operations']==1590
assert two['fault']['reason']==4 and two['fault']['boundary']=='memory-read' and two['active_import'] is None;assert int(two['fault']['source'],16)==0x10207bf94 and int(two['fault']['address'],16)==0 and two['fault']['width']==8;assert two['private_image_before_native_initialization']['guards']==29
rw_calls=[r for r in calls if r['event'] in ['import','import-return'] and r['target'] in [b['pc'] for b in contract['bindings'] if b['handler'].startswith('rwlock_')]];assert rw_calls and all(r['rax']==0 for r in rw_calls if r['event']=='import-return')
constructors=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in constructors};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(90)) and [r['ordinal'] for r in completed]==list(range(89));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
records=[]
for suffix in ['rwlock-reference-v1','rwlock-runtime-v1','rwlock-runtime-v2-repeat','startup-rwlock-windows-v1','ghidra-startup-rwlock-v1','rwlock-contract-v1','startup-rwlock-v1','startup-rwlock-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native rwlock services advance startup to an uninitialized FS-based thread-local read',current=two,authored=authored,contract=contract,completed_constructors=completed,entered_constructor=entered[-1],rwlock_calls=rw_calls,trace_events=len(calls),last_dispatch_event=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Constructor ordinal 89 is still in progress. Initial FS base remains zero; native TLS is required before proceeding.','Native ownership/default policies and opaque private-layout uncertainty remain explicit.','All original bytes remain NX, with 29 unresolved data/TLS guards and prior initialization/control/FP uncertainty.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],trace_events=len(calls),rwlock_calls=rw_calls)),flush=True)
