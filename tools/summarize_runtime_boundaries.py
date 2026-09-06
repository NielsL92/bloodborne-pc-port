"""Check private-memory and authored AOT runtime repeats and recorder identities."""
import argparse,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
checks=[]
for kind,first,repeat,run_first,run_repeat in [
 ('memory','memory-v2-deterministic','memory-v3-repeat','20260906-p3-runtime-memory-v2-deterministic','20260906-p3-runtime-memory-v3-repeat'),
 ('control','control-v4-deterministic','control-v5-repeat','20260906-p3-runtime-control-v4-deterministic','20260906-p3-runtime-control-v5-repeat')]:
 left=ROOT/'local/runtime'/first;right=ROOT/'local/runtime'/repeat
 x=json.loads((left/'summary.json').read_text());y=json.loads((right/'summary.json').read_text())
 for key in ['positive','negative','source_sha256']:assert x[key]==y[key],(kind,key)
 assert y['positive']['status']=='pass' and y['positive']['private_mappings_NX'] and not y['positive']['game_execution']
 artifacts={}
 for file in sorted(left.rglob('*')):
  if file.is_file() and (file.suffix in ['.obj','.bc'] or file.name in ['input.json','audit.json','runtime-entries.h','positive.stdout']):
   rel=file.relative_to(left);assert file.read_bytes()==(right/rel).read_bytes(),str(rel);artifacts[str(rel)]=sha(file)
 records=[]
 for run in [run_first,run_repeat]:
  folder=ROOT/'local/runs'/run;record=json.loads((folder/'manifest.json').read_text());assert record['status']=='pass' and record['exit_code']==0
  with zipfile.ZipFile(folder/'sources.zip') as snapshot:
   import hashlib
   for absolute,digest in y['source_sha256'].items():
    rel=Path(absolute).relative_to(ROOT).as_posix();assert record['source_sha256'][str(Path(rel))]==digest
    assert hashlib.sha256(snapshot.read(rel)).hexdigest()==digest
  records.append(dict(run=run,manifest_sha256=sha(folder/'manifest.json'),sources_zip_sha256=sha(folder/'sources.zip')))
 checks.append(dict(kind=kind,first=str(left),repeat=str(right),summary_sha256=sha(right/'summary.json'),positive=y['positive'],negative=y['negative'],identical_artifacts=artifacts,recorders=records))
summary=dict(status='repeated native runtime boundary evidence verified',checks=checks,limitations=['Authored AOT and private RAM fixtures only; no supplied game code execution.','Exact comparison covers COFF/bitcode/inputs/audits/stable results, not PE timestamps or runtime thread IDs.','Explicit process stops satisfy current nounwind boundary; guest exceptions/nonlocal recovery remain open.','No real native import service, FP profile, complete object linkage or native game startup established.'])
write_json(a.out/'checked.json',summary);print(json.dumps(dict(status=summary['status'],kinds=len(checks),identical_artifacts=sum(len(v['identical_artifacts']) for v in checks))),flush=True)
