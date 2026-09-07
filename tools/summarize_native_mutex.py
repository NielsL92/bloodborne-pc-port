"""Verify native mutex ownership and startup progress into constructor ordinal one."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
one,two=read(base/'startup-v10-mutex/summary.json'),read(base/'startup-v11-mutex-repeat/summary.json');assert stable(one)==stable(two)
artifacts={}
for path in (base/'startup-v10-mutex').iterdir():
 if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
  assert sha(path)==sha(base/'startup-v11-mutex-repeat'/path.name);artifacts[path.name]=sha(path)
x,y=read(base/'mutex-v1/summary.json'),read(base/'mutex-v2-repeat/summary.json');assert x==y and x['positive']['aot_service_calls']==53267
contract=read(base/'mutex-contract-v1/contract.json');assert sha(base/'mutex-contract-v1/contract.json')==two['native_service_contract_sha256'];assert two['native_service_bindings']==contract['bindings']
calls=[json.loads(s) for s in (base/'startup-v11-mutex-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==46;last=calls[-1];assert last['target']==0x102bbeaa8 and last['rsp']==0x700000fff18 and last['memory_operations']==418
for pc in [0x102bbfea8,0x102bbfeb8,0x102bbfec8,0x102bbfed8]:
 returns=[r for r in calls if r['target']==pc and r['event']=='import-return'];assert len(returns)==2 and all(r['rax']==0 for r in returns)
assert two['fault']['reason']==25 and two['active_import']['nid']=='pO96TwzOm5E';assert two['private_image_before_native_initialization']['guards']==29
constructors=json.loads(Path('local/cfg/startup-v1/roots.json').read_text());ctor0=0x100000000+constructors[0]['target'];ctor1=0x100000000+constructors[1]['target'];assert any(r['event']=='dispatch-return' and r['target']==ctor0 and r['pc']==0x100000084 for r in calls);assert any(r['event']=='dispatch' and r['target']==ctor1 for r in calls);assert not any(r['event']=='dispatch-return' and r['target']==ctor1 for r in calls);assert sum(r['event']=='import-return' and r['target']==0x102bbfef8 and r['rax']==0 for r in calls)==1
records=[]
for suffix in ['mutex-runtime-v1','mutex-runtime-v2-repeat','mutex-reference-v1','startup-mutex-windows-v3-ownership','ghidra-startup-mutex-v3-ownership','mutex-contract-v1','startup-mutex-v1','startup-mutex-v2-repeat']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native mutex creation and ownership advance startup into constructor ordinal one',current=two,completed_constructor=constructors[0],entered_constructor=constructors[1],contract=contract,authored=x,trace_events=len(calls),last_call=last,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Constructor ordinal zero returned and ordinal one entered. The trace stops at direct-memory size inquiry; no main or boot is claimed.','Mutex and attribute objects use native process state and logical identifiers. Private guest layouts, static/named/timed/robust/protocol interfaces remain explicit unsupported boundaries.','Native defaults and resource limits are documented compatibility policies, not console observations.','Twenty-nine data/TLS guards and all prior startup/control uncertainties remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],bindings=len(contract['bindings']),trace_events=len(calls),next_import=two['active_import'])),flush=True)
