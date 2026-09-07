"""Check exact native startup repeats and report only observed constructor/accessor progress."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('repeat',type=Path);p.add_argument('out',type=Path);p.add_argument('--batch',nargs=2,type=Path,action='append',default=[]);p.add_argument('--cfg',nargs=2,type=Path,action='append',default=[]);p.add_argument('--recovery',nargs=2,type=Path,action='append',default=[]);p.add_argument('--run',action='append',default=[]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='thread'}
 if isinstance(v,list):return [stable(x) for x in v]
 return v
summary=read(a.repeat/'summary.json');assert stable(summary)==stable(read(a.first/'summary.json'));assert summary['game_aot_execution'] and not summary['original_byte_cpu_execution'] and not summary['native_game_boot'];artifacts={}
for path in a.first.iterdir():
 if path.suffix in ['.obj','.exe','.bin'] or path.name in ['probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','compilation-objects.json','compilation-targets.json','native-calls.jsonl','prepare.stdout','entry.stdout']:
  assert sha(path)==sha(a.repeat/path.name);artifacts[path.name]=sha(path)
assert sha(a.repeat/'startup.exe')==summary['executable_sha256'];assert sha(a.repeat/'native-calls.jsonl')==summary['control_trace_sha256']
objects=read(a.repeat/'compilation-objects.json');targets=read(a.repeat/'compilation-targets.json');assert len(objects)==summary['compiled_objects'] and len(targets)==summary['compiled_roots'];assert len({r['pc'] for r in targets})==len(targets)
calls=[json.loads(s) for s in (a.repeat/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];roots=read('local/cfg/startup-v1/roots.json');lookup={0x100000000+r['target']:r for r in roots};assert len(lookup)==len(roots)
# The supplied initializer dispatch has one consistent stack context in this probe.
constructor_rsp=0x700000fff88;constructor_rbp=0x700000fffb0
entered=[lookup[r['target']] for r in calls if r['event']=='dispatch' and r['target'] in lookup and r['rsp']==constructor_rsp and r['rbp']==constructor_rbp];completed=[lookup[r['target']] for r in calls if r['event']=='dispatch-return' and r['target'] in lookup and r['pc']==0x100000084 and r['rsp']==constructor_rsp+8 and r['rbp']==constructor_rbp];assert [r['ordinal'] for r in entered]==list(range(len(entered))) and [r['ordinal'] for r in completed]==list(range(len(completed)));assert len(entered) in [len(completed),len(completed)+1]
batches=[]
for first,repeat in a.batch:
 b=read(repeat/'summary.json');assert b==read(first/'summary.json') and b['validation_kind']=='conditional-simple-leaf-batch'
 for name,digest in {**b['files'],**b['native_objects']}.items():assert sha(first/name)==sha(repeat/name)==digest
 assert any(o['sha256']==b['files']['function.obj'] for o in objects);returns=[r for r in calls if r['event']=='dispatch-return' and r['target'] in b['compiled_roots']];addresses={leaf['pc']:leaf['address'] for leaf in b['leaves'] if leaf['width']==0};assert all(r['rax']==addresses[r['target']] for r in returns if r['target'] in addresses);batches.append(dict(validation=b,actual_returns=returns,unobserved_roots=sorted(set(b['compiled_roots'])-{r['target'] for r in returns})))
cfgs=[]
from tools.native_supplement_contract import validate
for first,repeat in a.cfg:
 b=read(repeat/'summary.json');assert b==read(first/'summary.json');validate(b,repeat)
 for name,digest in b['files'].items():assert sha(first/name)==sha(repeat/name)==digest
 assert any(o['sha256']==b['files']['function.obj'] for o in objects);events=[r for r in calls if r['target'] in b['compiled_roots']];cfgs.append(dict(validation=b,actual_events=events,unobserved_roots=sorted(set(b['compiled_roots'])-{r['target'] for r in events})))
recoveries=[]
for first,repeat in a.recovery:
 files=['analysis.sqlite','identity.json','delta.json','summary.json','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json','windows.json','prior-overlaps.json'];hashes={name:sha(first/name) for name in files};assert all(sha(repeat/name)==digest for name,digest in hashes.items());recoveries.append(dict(delta=read(repeat/'delta.json'),files=hashes))
recorders=[]
for run in a.run:
 folder=Path('local/runs')/run;r=read(folder/'manifest.json');assert r['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in r['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 recorders.append(dict(run=run,start_utc=r['start_utc'],end_utc=r['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native startup repeat and observed progress checked',current_probe=str(a.repeat),current=summary,artifacts=artifacts,batches=batches,cfgs=cfgs,recoveries=recoveries,completed_constructors=completed,entered_constructors=entered,trace_events=len(calls),last_call=calls[-1],recorders=recorders,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Constructor counts require the checked initializer stack context and return address. The trace does not enumerate every instruction or static call.','Conditional pointer candidates retain their original provenance; actual returns are listed separately. No table extent, mutability, pointed-to layout or discovery closure is inferred.','P4 and previous startup, service, TLS/FP, control and baseline limitations remain open.']);write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],current_probe=str(a.repeat),completed_constructors=len(completed),entered_constructors=len(entered),last_call=calls[-1],executable_sha256=summary['executable_sha256'])),flush=True)
