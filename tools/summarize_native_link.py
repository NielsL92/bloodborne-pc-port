"""Verify complete static linkage, explicit stops, repeatability and runtime provenance."""
import argparse,json,hashlib,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
artifacts={}
for left,right in [('registry-v2-ghidra','registry-v3-repeat'),('link-v4-import-stops','link-v5-repeat')]:
 x=ROOT/'local/runtime'/left;y=ROOT/'local/runtime'/right
 selected=[p for p in x.iterdir() if p.is_file() and (left.startswith('registry') or p.suffix in ['.obj','.exe'] or p.name in ['linked-addresses.json','native-import-stops.json','validate.stdout'])]
 for path in selected:assert path.read_bytes()==(y/path.name).read_bytes(),path.name;artifacts[left+'/'+path.name]=sha(path)
reg=ROOT/'local/runtime/registry-v3-repeat';linked=ROOT/'local/runtime/link-v5-repeat';summary=read(linked/'summary.json');registry=read(reg/'summary.json');assert summary['objects']==386 and summary['linked_game_roots']==21282 and summary['linked_import_gateways']==182 and summary['tested_unimplemented_import_stops']==115
assert not summary['game_execution'] and not summary['runtime_validation']['game_entry_called'] and not summary['runtime_validation']['guest_mappings_created']
assert registry['compiled_export_bindings']==67 and registry['explicit_native_stops']==115 and registry['source_pairs']==551 and len(registry['unresolved_x87_sites'])==14
records=[]
for suffix in ['registry-v2-ghidra','registry-v3-repeat','link-v4-import-stops','link-v5-repeat']:
 folder=ROOT/'local/runs'/('20260906-p3-native-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as snapshot:
  for name,digest in record['source_sha256'].items():
   if name.startswith('native\\runtime\\') or name in ['tools\\native_registry.py','tools\\native_link.py']:
    assert hashlib.sha256(snapshot.read(Path(name).as_posix())).hexdigest()==digest
 records.append(dict(run=folder.name,manifest_sha256=sha(folder/'manifest.json'),sources_zip_sha256=sha(folder/'sources.zip')))
# Complete link uses the same core runtime and numerical sources as the authored FP run.
fp=read(ROOT/'local/runs/20260906-p3-runtime-fp-v3-repeat/manifest.json');last=read(ROOT/'local/runs/20260906-p3-native-link-v5-repeat/manifest.json')
core=['native/runtime/'+name for name in ['runtime.h','fault.cpp','memory.cpp','control.cpp','intrinsics.cpp','fp.cpp']]+['native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h']
for name in core:assert fp['source_sha256'][str(Path(name))]==last['source_sha256'][str(Path(name))]
gate=dict(phase='P3 startup compilation and explicit exit handling',passed=True,basis=['All 18,444 ordered initial constructors are retained exactly once in the independently checked complete object manifest.','All 386 objects link with all 21,282 compiled roots, 182 import gateways and 63 support/library names resolved.','Static source/request authorization has 551 independently decoded pairs; runtime authored control/fault contracts and complete-registry unknown/native-service stops are validated.','Registry, native objects and complete PE repeat byte-for-byte; no game CPU execution was used to establish this gate.'],limits=['This is the plan compilation/explicit-handling gate, not complete runtime service/control implementation or execution coverage.','9,044 unknown indirect calls, 430 indirect jumps, 143 callback arguments, five conditional continuations and three native service-control obligations remain visible.','14 x87 sites have independently checked instruction boundaries but unresolved default selector metadata and stop if reached.','67 compiled-export bindings remain conditional on immutable module identity, relocation/loading, initialization and interposition assumptions.','115 external native services, hypercalls, FP profile selection, guest exceptions/nonlocal transfer, loader and startup remain P4 work.'])
result=dict(status='complete native linkage and P3 startup compilation gate checked',linkage=summary,registry=registry,identical_artifacts=artifacts,recorders=records,gate=gate,next_phase='P4 module loading as private NX data and native startup/service integration',game_execution=False)
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],p3_gate_passed=True,identical_artifacts=len(artifacts),game_execution=False)),flush=True)
