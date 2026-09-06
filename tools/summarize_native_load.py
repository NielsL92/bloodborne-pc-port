"""Verify native loader repeat, independent byte digest and immutable input identities."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
x=ROOT/'local/runtime/load-v2-sha-width';y=ROOT/'local/runtime/load-v3-repeat';one=read(x/'summary.json');two=read(y/'summary.json');assert one==two
artifacts={}
for path in x.iterdir():
 if path.suffix in ['.obj','.bin'] or path.name in ['expected.json','guards.json','authored.stdout','game-data.stdout']:
  assert sha(path)==sha(y/path.name),path.name;artifacts[path.name]=sha(path)
assert two['actual']['mapped_bytes']==97517568 and two['actual']['verified_bytes']==97517272 and two['actual']['guarded_bytes']==296;assert two['actual']['relocations']==238572 and two['actual']['guards']==two['unresolved_guard_probes']==37;assert len(two['setup_rejections'])==11
plan=ROOT/'local/runtime/loader-plan-v8-memory';assert two['plan_sha256']==sha(plan/'summary.json');assert sha(y/'modules.bin')==two['bundle_sha256'];records=[]
for suffix in ['native-load-v1','native-load-v2-sha-width','native-load-v3-repeat']:
 folder=ROOT/'local/runs'/('20260906-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']==('failed' if suffix=='native-load-v1' else 'pass')
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,status=record['status'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
for module in read(plan/'modules.json'):assert sha(module['path'])==module['module']
result=dict(status='repeated private native loader verified',load=two,identical_artifacts=artifacts,recorders=records,game_execution=False,p4_gate_passed=False,limits=['The failed first compile used an unavailable Windows integer-limit macro; its output/source snapshot is preserved.','Exact repeat covers bundles, native objects and validation outputs; standalone fixture PE timestamps are not normalized.','All supplied module hashes remain unchanged. Original packages and hardlinked game views were never written.','Game byte mappings exist only as private NX data. No game-derived CPU function, initializer, callback or service executes in this loader fixture.','Initialization order, logical stack/TLS, real services, target FP profile, guest exception/nonlocal transfer and first native entry remain open.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],identical_artifacts=len(artifacts),actual=two['actual'])),flush=True)
