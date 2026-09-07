"""Verify direct-memory backing, mapping, and the native observed-target stop."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v12-direct-memory/summary.json'),read(base/'startup-v13-direct-memory-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v12-direct-memory').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v13-direct-memory-repeat'/path.name);artifacts[path.name]=sha(path)
x,y=read(base/'direct-memory-v1/summary.json'),read(base/'direct-memory-v2-repeat/summary.json');assert x==y and x['positive']['aot_service_calls']==4302
contract=read(base/'direct-memory-contract-v1/contract.json');assert sha(base/'direct-memory-contract-v1/contract.json')==two['native_service_contract_sha256'];assert two['native_service_bindings']==contract['bindings']
calls=[json.loads(s) for s in (base/'startup-v13-direct-memory-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==251;last=calls[-1];assert last['target']==0x10207f3b0 and last['rsp']==0x700000ffed8 and last['memory_operations']==1205
for pc in [0x102bbeaa8,0x102bbeab8,0x102bbeac8]:
 returns=[r for r in calls if r['target']==pc and r['event']=='import-return'];assert len(returns)==1 and returns[0]['rax']==(0x120000000 if pc==0x102bbeaa8 else 0)
allocation=next(r for r in calls if r['event']=='import' and r['target']==0x102bbeab8);mapping=next(r for r in calls if r['event']=='import' and r['target']==0x102bbeac8);assert [allocation[k] for k in ['rdi','rsi','rdx','rcx','r8']]==[0,0x120000000,0x7400000,0x200000,0];assert [mapping[k] for k in ['rsi','rdx','rcx','r8','r9']]==[0x7400000,3,0,0,0x200000]
assert two['fault']['reason']==27 and two['fault']['boundary']=='unknown-compiled-target' and two['active_import'] is None;assert two['private_image_before_native_initialization']['guards']==29
constructors=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in constructors};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(90)) and [r['ordinal'] for r in completed]==list(range(89));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
records=[]
for suffix in ['direct-memory-runtime-v1','direct-memory-runtime-v2-repeat','memory-v8-dynamic-regression','startup-dmem-windows-v1','ghidra-startup-dmem-v1','direct-memory-contract-v1','startup-direct-memory-v1','startup-direct-memory-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native direct memory advances startup through 89 constructors to an unknown compiled target',current=two,completed_constructors=completed,entered_constructor=entered[-1],allocation_call=allocation,mapping_call=mapping,contract=contract,authored=x,trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Constructors 0-88 returned and ordinal 89 entered. An unknown compiled target at 0x10207f3b0 stops execution; no main or boot is claimed.','Native memory type zero, zero-hint RW mappings and exact unmapped release are bounded interfaces. GPU/flexible memory, other flags/types/hints and unmapping/partial/mapped release remain open.','Native defaults and resource limits are documented compatibility policies, not console observations.','Twenty-nine data/TLS guards and all prior startup/control uncertainties remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],bindings=len(contract['bindings']),trace_events=len(calls),unknown_target=two['fault']['actual'],completed_constructors=len(completed))),flush=True)
