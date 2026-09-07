"""Verify native mutex-attribute state, exact bindings, and the next repeated startup stop."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v8-mutexattr/summary.json'),read(base/'startup-v9-mutexattr-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v8-mutexattr').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v9-mutexattr-repeat'/path.name);artifacts[path.name]=sha(path)
x,y=read(base/'mutexattr-v1/summary.json'),read(base/'mutexattr-v2-repeat/summary.json');assert x==y and x['positive']['aot_service_calls']==45059
contract=read(base/'mutexattr-contract-v1/contract.json');assert sha(base/'mutexattr-contract-v1/contract.json')==two['native_service_contract_sha256'];assert two['native_service_bindings']==contract['bindings'];assert len(contract['bindings'])==9
calls=[json.loads(s) for s in (base/'startup-v9-mutexattr-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==17;last=calls[-1];assert last['target']==0x102bbfec8 and last['rdi']==0x1056a5728 and last['rsi']==0x700000fff48 and last['rdx']==0 and last['memory_operations']==154
for pc in [0x102bbfea8,0x102bbfeb8]:
 returns=[r for r in calls if r['target']==pc and r['event']=='import-return'];assert len(returns)==1 and returns[0]['rax']==0
assert two['fault']['reason']==25 and two['active_import']['nid']=='cmo1RIYva9o';assert two['private_image_before_native_initialization']['guards']==29
records=[]
for suffix in ['mutexattr-runtime-v1','mutexattr-runtime-v2-repeat','mutexattr-reference-v1','startup-mutex-windows-v2-full','ghidra-startup-mutex-v2-full','mutexattr-contract-v1','startup-mutexattr-v1','startup-mutexattr-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native mutex attributes advance the first constructor to explicit mutex creation',current=two,contract=contract,authored=x,trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['The first constructor has not returned. Mutex creation and locking remain unimplemented.','Attribute objects are native process state identified by opaque logical handles. Direct guest reads of private attribute layout remain explicit stops.','Native defaults and resource limits are documented compatibility policies, not console observations.','Twenty-nine data/TLS guards and all prior startup/control uncertainties remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],bindings=len(contract['bindings']),trace_events=len(calls),next_import=two['active_import'])),flush=True)
