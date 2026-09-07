"""Verify four observed RIP-address leaves, their run chain, and constructor progress."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
chain=read('local/runtime/address-chain-v1/summary.json');assert len(chain['advances'])==3
assert stable(read('local/runtime/startup-v24-address-leaf/summary.json'))==stable(read('local/runtime/startup-v25-address-leaf-repeat/summary.json'))
for name in ['input.json','audit.json','function.bc','function.obj']:assert sha(Path('local/compiler-spike/native-leaf-2375af0-v2-repeat')/name)==sha(Path('local/compiler-spike/native-leaf-2375af0-v3-address-regression')/name)
leaf_dirs=[Path('local/compiler-spike/native-leaf-2375b10-v2-repeat')]+[Path(r['compiled']) for r in chain['advances']];leaves=[]
for folder in leaf_dirs:
 d=read(folder/'summary.json');assert d['address_form'] and d['positive']['cases']==3072 and d['negative_stops']==2 and d['load_width']==0
 for name,digest in d['files'].items():assert sha(folder/name)==digest
 inspection=read(folder/'inspection.json');assert inspection['memory_source_audit']['counts']=={'__bb_sourced_read_memory_64':1};assert {int(s,16) for s in inspection['memory_source_audit']['source_pcs']}=={d['compiled_roots'][0]+7};leaves.append(d)
assert [d['compiled_roots'][0] for d in leaves]==[0x102375b10,0x102375b20,0x102375b30,0x102375b40]
for step in chain['advances']:
 folder=Path(step['current']);assert sha(folder/'summary.json')==step['summary_sha256']
 for name,digest in step['artifacts'].items():assert sha(folder/name)==digest
current=Path(chain['current_probe']);summary=read(current/'summary.json');assert summary['compiled_objects']==393 and summary['compiled_roots']==21289 and len(summary['supplements'])==7
calls=[json.loads(s) for s in (current/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];assert len(calls)==387 and calls[-1]['target']==0x102370950 and calls[-1]['memory_operations']==2325
roots=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in roots};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(94)) and [r['ordinal'] for r in completed]==list(range(93));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
returns=[r for r in calls if r['event']=='dispatch-return' and r['target'] in [d['compiled_roots'][0] for d in leaves]];assert {r['target'] for r in returns}=={d['compiled_roots'][0] for d in leaves};assert all(r['rax']==next(d['constant_address'] for d in leaves if d['compiled_roots'][0]==r['target']) for r in returns)
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
names=['recover-native-address-leaf-v1','ghidra-native-address-leaf-v1','compile-native-address-leaf-v1','compile-native-address-leaf-v2-repeat','native-qword-leaf-address-regression','native-address-leaf-manifest-v1','startup-address-leaf-v1','startup-address-leaf-v2-repeat','address-chain-v1'];run_ids=['20260907-p4-'+name for name in names]+[r['run'] for r in chain['steps']];recorders=[]
for name in run_ids:
 folder=Path('local/runs')/name;r=read(folder/'manifest.json');assert r['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in r['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 recorders.append(dict(run=name,start_utc=r['start_utc'],end_utc=r['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(preserved_report_failure=dict(run='20260907-p4-native-address-leaves-evidence-v1',reason='Initial checker incorrectly expected all four distinct RIP-relative displacements to return one address; corrected to each independently decoded expected address.'),status='four checked RIP-address leaves advance native startup through 93 constructors',current=summary,current_probe=str(current),chain=chain,leaves=leaves,completed_constructors=completed,entered_constructor=entered[-1],leaf_returns=returns,trace_events=len(calls),last_call=calls[-1],recorders=recorders,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Only observed targets are added after independent decoding and repeat checks. Nearby entries were not inferred as executable callbacks.','The returned logical address is not dereferenced by these accessors; no pointed-to object identity or layout is proven by returning it.','The last constructor is ordinal 93, still in progress. Native startup/FP/dynamic TLS, unknown callbacks, exceptions/nonlocal flow and other prior limitations remain.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],current_probe=str(current),executable_sha256=summary['executable_sha256'],executable_bytes=summary['executable_bytes'],entered_constructor=entered[-1]['ordinal'])),flush=True)
