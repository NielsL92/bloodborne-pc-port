"""Publish an additive native target manifest after exact independent compile repeats."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('repeat',type=Path);p.add_argument('registry',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
r=read(a.repeat/'summary.json');assert r==read(a.first/'summary.json');assert r['base_registry_identity']==sha(a.registry/'identity.json');assert r['status']=='supplemental supplied leaf compiled and native semantics checked';assert not r['source_pairs'] and not r['imports'];assert r['positive']['cases']==3072 and r['negative_stops']==2
assert r['lifter_sha256']==sha(ROOT/'build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe') and r['semantics_sha256']==sha(ROOT/'build/extended-semantics-v35-divide/amd64_avx.bc');assert sha(r['module']['path'])==r['module']['module']
for name,digest in {**r['files'],**r['native_objects']}.items():assert sha(a.first/name)==sha(a.repeat/name)==digest
base=read(a.registry/'targets.json')+read(a.registry/'imports.json');assert not set(r['compiled_roots'])&{t['pc'] for t in base}
manifest=dict(schema=1,base_registry_identity=r['base_registry_identity'],module=r['module'],compiled_roots=r['compiled_roots'],source_pairs=[],imports=[],object_path=str((a.repeat/'function.obj').resolve()),object_sha256=sha(a.repeat/'function.obj'),validation_path=str((a.repeat/'summary.json').resolve()),validation_sha256=sha(a.repeat/'summary.json'),input_sha256=sha(a.repeat/'input.json'),audit_sha256=sha(a.repeat/'audit.json'),bitcode_sha256=sha(a.repeat/'function.bc'),first_validation_sha256=sha(a.first/'summary.json'),source_db_sha256=read(a.repeat/'recovery.json')['source_db_sha256'],lifter_sha256=r['lifter_sha256'],semantics_sha256=r['semantics_sha256'],scope='Additive two-instruction ordinary-return body; base imports, source pairs, recovery records and uncertainty are unchanged.')
write_json(a.out/'manifest.json',manifest);write_json(a.out/'summary.json',dict(status='exact repeated native target supplement manifest published',manifest_sha256=sha(a.out/'manifest.json'),new_objects=1,new_entries=1,new_roots=1,new_instructions=2,combined_objects=387,combined_roots=21283,game_execution=False,native_game_boot=False));print('Supplement manifest checked and published')
