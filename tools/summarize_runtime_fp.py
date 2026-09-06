"""Verify repeated FP runtime linkage fixtures and memory/control regressions."""
import argparse,json,zipfile,hashlib
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
x=ROOT/'local/runtime/fp-v2-payloads';y=ROOT/'local/runtime/fp-v3-repeat';left=json.loads((x/'summary.json').read_text());right=json.loads((y/'summary.json').read_text());assert left==right
artifacts={}
for path in sorted(x.iterdir()):
 if path.suffix in ['.obj','.bc'] or path.name in ['input.json','sites.json','audit.json','runtime-fp-entries.h','positive.stdout']:
  assert path.read_bytes()==(y/path.name).read_bytes(),path.name;artifacts[path.name]=sha(path)
records=[]
for suffix in ['fp-v2-payloads','fp-v3-repeat','memory-v4-fp-regression','control-v6-fp-regression']:
 folder=ROOT/'local/runs'/('20260906-p3-runtime-'+suffix);record=json.loads((folder/'manifest.json').read_text());assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as snapshot:
  for absolute,digest in right['source_sha256'].items():
   rel=Path(absolute).relative_to(ROOT);assert record['source_sha256'][str(rel)]==digest;assert hashlib.sha256(snapshot.read(rel.as_posix())).hexdigest()==digest
 records.append(dict(run=folder.name,manifest_sha256=sha(folder/'manifest.json'),source_zip_sha256=sha(folder/'sources.zip')))
summary=dict(status='native FP runtime repeated artifacts and regressions verified',fp=right,identical_artifacts=artifacts,recorders=records,memory=json.loads((ROOT/'local/runtime/memory-v4-fp-regression/summary.json').read_text())['positive'],control=json.loads((ROOT/'local/runtime/control-v6-fp-regression/summary.json').read_text())['positive'])
write_json(a.out/'checked.json',summary);print(json.dumps(dict(status=summary['status'],identical_artifacts=len(artifacts))),flush=True)
