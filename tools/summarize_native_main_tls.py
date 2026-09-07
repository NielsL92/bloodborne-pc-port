"""Verify main static TLS initialization and the next native target dependency."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v18-main-tls/summary.json'),read(base/'startup-v19-main-tls-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v18-main-tls').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v19-main-tls-repeat'/path.name);artifacts[path.name]=sha(path)
authored=read('local/runtime/main-tls-v3-repeat/summary.json');assert authored==read('local/runtime/main-tls-v2-name/summary.json');assert authored['positive']['aot_calls']==3752 and authored['negative_stops']==3
contract=read('local/runtime/main-tls-contract-v1/contract.json');assert sha(Path('local/runtime/main-tls-contract-v1/contract.json'))==two['main_tls_contract_sha256'] and two['main_tls']==contract
calls=[json.loads(s) for s in (base/'startup-v19-main-tls-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==315;last=calls[-1];assert last['memory_operations']==1748 and last['target']==0x102375af0 and last['rsp']==0x700000ffea8
assert two['fault']['reason']==27 and two['fault']['boundary']=='unknown-compiled-target' and two['active_import'] is None;assert two['private_image_before_native_initialization']['guards']==30
prepared=read(base/'startup-v19-main-tls-repeat/prepare.stdout');assert prepared['native_main_tls_initialized'] and int(prepared['fs_base'],16)==0x74000010000
constructors=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in constructors};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(90)) and [r['ordinal'] for r in completed]==list(range(89));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
records=[]
for suffix in ['tls-references-v1','startup-tls-windows-v1','ghidra-startup-tls-v1','native-tls-scan-v1','main-tls-runtime-v2-name','main-tls-runtime-v3-repeat','main-tls-contract-v1','startup-main-tls-v1','startup-main-tls-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
failed=read('local/runs/20260907-p4-main-tls-runtime-v1/manifest.json');assert failed['status']=='failed'
result=dict(status='main static TLS advances native startup to another unknown compiled target',current=two,authored=authored,contract=contract,scan=read('local/runtime/tls-scan-v1/summary.json'),completed_constructors=completed,entered_constructor=entered[-1],trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,preserved_failure=dict(run='20260907-p4-main-tls-runtime-v1',manifest_sha256=sha('local/runs/20260907-p4-main-tls-runtime-v1/manifest.json'),reason='Fixture SIZE identifier collided with the Windows SIZE type. Renamed TLS_BYTES before successful repeated builds.'),game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Constructor ordinal 89 remains in progress. The next missing target is 0x102375af0.','Main static TLS/self-pointer only; 29 prior data/TLS guards plus one guard for unsupported TCB fields remain.','No dynamic-module TLS, guest thread creation, full initialization/FP/control closure or native boot is claimed.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],trace_events=len(calls))),flush=True)
