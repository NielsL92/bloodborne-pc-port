"""Verify grouped leaf provenance, independent builds and actual native constructor progress."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
chain=read('local/runtime/accessor-chain-v2/summary.json');assert len(chain['advances'])==3
for step in chain['advances']:
 folder=Path(step['current']);assert sha(folder/'summary.json')==step['summary_sha256']
 for name,digest in step['artifacts'].items():assert sha(folder/name)==digest
first=Path('local/compiler-spike/pointer-leaves-compile-v1');repeat=Path('local/compiler-spike/pointer-leaves-compile-v2-repeat');batch=read(repeat/'summary.json');assert batch==read(first/'summary.json') and batch['positive']['cases']==9216 and batch['negative_stops']==6
for name,digest in {**batch['files'],**batch['native_objects']}.items():assert sha(first/name)==sha(repeat/name)==digest
recovery=read(repeat/'recovery.json');assert [b['observed_requested_entry'] for b in recovery['bodies']]==[True,False,False];assert [b['pc'] for b in recovery['bodies']]==[0x102370980,0x102370990,0x1023709a0];assert len(recovery['slots'])==13
one=Path('local/runtime/startup-v38-pointer-leaves');current=Path('local/runtime/startup-v39-pointer-leaves-repeat');summary=read(current/'summary.json');assert stable(summary)==stable(read(one/'summary.json'));artifacts={}
for path in one.iterdir():
 if path.suffix in ['.obj','.exe','.bin'] or path.name in ['probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','compilation-objects.json','compilation-targets.json','native-calls.jsonl','prepare.stdout','entry.stdout']:
  assert sha(path)==sha(current/path.name);artifacts[path.name]=sha(path)
assert summary['compiled_objects']==397 and summary['compiled_roots']==21295 and len(summary['supplements'])==11
calls=[json.loads(s) for s in (current/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];assert len(calls)==415 and calls[-1]['target']==0x10236f6f0 and calls[-1]['memory_operations']==2726
roots=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in roots};entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup];assert [r['ordinal'] for r in entered]==list(range(98)) and [r['ordinal'] for r in completed]==list(range(97));assert all(r['pc']==0x100000084 for r in calls if r['event']=='dispatch-return' and r['target'] in lookup)
leaves=[read(Path(step['compiled'])/'summary.json') for step in chain['advances']];all_roots={b['pc'] for b in batch['leaves']}|{pc for leaf in leaves for pc in leaf['compiled_roots']};returns=[r for r in calls if r['event']=='dispatch-return' and r['target'] in all_roots];assert {r['target'] for r in returns}==all_roots
addresses={b['pc']:b['address'] for b in batch['leaves'] if b['width']==0};addresses.update({leaf['compiled_roots'][0]:leaf['constant_address'] for leaf in leaves if leaf['address_form']});assert all(r['rax']==addresses[r['target']] for r in returns if r['target'] in addresses)
for leaf in leaves:
 assert leaf['positive']['cases']==3072 and leaf['negative_stops']==2
for m in read('local/runtime/loader-plan-v9-runtime-word/modules.json'):assert sha(m['path'])==m['module']
assert sha('local/cfg/startup-recovery-v31-conditional-repeat/analysis.sqlite')==recovery['source_db_sha256']
run_ids=['20260907-p4-accessor-chain-v2']+[r['run'] for r in chain['steps']]+['20260907-p4-'+s for s in ['pointer-leaf-recovery-v1','pointer-leaf-ghidra-v1','pointer-leaf-compile-v1','pointer-leaf-compile-v2-repeat','pointer-leaf-manifest-v1','startup-pointer-leaves-v1','startup-pointer-leaves-v2-repeat']];recorders=[]
for name in run_ids:
 folder=Path('local/runs')/name;r=read(folder/'manifest.json');assert r['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in r['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 recorders.append(dict(run=name,start_utc=r['start_utc'],end_utc=r['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='six checked accessors advance native startup through 97 constructors',current_probe=str(current),current=summary,artifacts=artifacts,observed_chain=chain,batch=batch,recovery=recovery,completed_constructors=completed,entered_constructor=entered[-1],leaf_returns=returns,trace_events=len(calls),last_call=calls[-1],recorders=recorders,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=recovery['limitations']+['All three batch candidates subsequently return in this startup trace; this observation does not establish table extent, mutability, other candidate bodies or execution coverage elsewhere.','P4, complete startup ABI/FP/dynamic TLS, unknown callbacks, exceptions/nonlocal flow and prior runtime limitations remain open.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],current_probe=str(current),executable_sha256=summary['executable_sha256'],entered_constructor=entered[-1]['ordinal'])),flush=True)
