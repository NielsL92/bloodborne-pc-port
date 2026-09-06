"""Verify guard/source diagnostics, preserved counterexample and native regressions."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
base=ROOT/'local/runtime';x=base/'guards-v3-flow';y=base/'guards-v4-repeat';left=read(x/'summary.json');right=read(y/'summary.json');assert left==right
artifacts={}
for path in sorted(x.iterdir()):
 if path.suffix in ['.obj','.bc'] or path.name in ['input.json','audit.json','guard-entries.h','positive.stdout']:
  assert path.read_bytes()==(y/path.name).read_bytes(),path.name;artifacts[path.name]=sha(path)
assert right['positive']['aot_cases']==2568 and right['positive']['unguarded_spans']==648
old=[json.loads(s) for s in (base/'guards-v1/aot-read-121-8.stderr').read_text().splitlines()]
assert int(old[0]['source'],16)==0x1000e0000 and old[1]['completed_memory_operations']==0
fixed=[json.loads(s) for s in (y/'aot-read-121-8.stderr').read_text().splitlines()];assert int(fixed[0]['source'],16)==int(fixed[0]['pc'],16)==0x1000e0001 and fixed[1]['completed_memory_operations']==0
regressions={}
for before,after in [('memory-v4-fp-regression','memory-v5-guards'),('control-v6-fp-regression','control-v7-memory-sources'),('fp-v3-repeat','fp-v4-memory-sources')]:
 one=read(base/before/'summary.json');two=read(base/after/'summary.json');assert one['positive']==two['positive'] and one['negative']==two['negative'];regressions[after]=dict(positive=two['positive'],negative_cases=len(two['negative']))
records=[]
for name,status in [('20260906-p4-runtime-guards-v1','failed')]+[('20260906-p4-runtime-'+s,'pass') for s in ['guards-v2-sourced','guards-v3-flow','guards-v4-repeat','memory-v5-guards','control-v7-memory-sources','fp-v4-memory-sources']]:
 folder=ROOT/'local/runs'/name;record=read(folder/'manifest.json');assert record['status']==status,(name,record['status'])
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=name,status=status,manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
lifter=ROOT/'build/sparse-lift-v12-memory-sources';identity=read(lifter/'identity.json');assert identity['driver_source_sha256']==sha(ROOT/'native/sparse_lift/main.cpp');assert identity['executable_sha256']==sha(lifter/'bb-sparse-lift.exe')
summary=dict(status='native unresolved-slot guards and precise authored instruction sources verified',guards=right,identical_artifacts=artifacts,regressions=regressions,preserved_counterexample=dict(run='20260906-p4-runtime-guards-v1',reported_source=0x1000e0000,required_source=0x1000e0001,completed_operations=0),recorders=records,compiler=identity,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native/runtime').glob('*') if p.is_file()},native_game_execution=False,active_game_objects_migrated=False,limitations=['Guarded slots are unresolved, not initialized to a guessed semantic value.','Successful bridges retain architectural State; terminating faults obtain explicit State and executed source PC. Scopes never cover dispatch into another compiled function.','Authored fixture ABI migration does not migrate current game objects; whole-set recompilation, LLVM checks and linkage are required before native startup.','No guest exception recovery, target FP profile, native module loading, boot or gameplay.'])
write_json(a.out/'checked.json',summary);print(json.dumps(dict(status=summary['status'],negative_cases=len(right['negative']),identical_artifacts=len(artifacts),regressions=regressions)),flush=True)
