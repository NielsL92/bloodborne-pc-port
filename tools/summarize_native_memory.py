"""Verify startup memory-source ABI migration, independent audit and complete linkage."""
import argparse,collections,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
base=ROOT/'local/compiler-spike';runtime=ROOT/'local/runtime';manifest=base/'native-memory-manifest-v1';migration=read(manifest/'evidence.json');inventory=read(base/'control-exit-inventory-v11-memory/summary.json');prior=read(base/'control-exit-inventory-v10-source-repeat/summary.json');assert inventory['active_manifest_sha256']==migration['active_manifest_sha256']==sha(manifest/'active-objects.json');assert inventory['memory_source_counts']==migration['compiler_bridge_counts']
for key in ['site_counts','cfg_reachable_site_counts','cfg_unreachable_site_counts']:
 normalized={name.replace('__bb_sourced_','__bb_native_'):count for name,count in inventory[key].items()};assert normalized==prior[key],key
assert inventory['indirect_llvm_calls']==0
for row in read(base/'control-exit-inventory-v11-memory/objects.json'):
 path=base/'control-exit-inventory-v11-memory'/f"object-{row['index']:04d}.json";assert sha(path)==row['report_sha256'];audit=read(path)['memory_source_audit'];assert not audit['invalid_sites'] and not audit['legacy_memory_calls']
for name in ['source-target-pairs.json','native-import-stubs.json','ghidra-tail-windows.json']:assert sha(base/'source-exit-dispatch-v3-memory'/name)==sha(base/'source-exit-dispatch-v2-tail-imports'/name)
artifacts={}
for first,second in [('registry-v6-memory','registry-v7-memory-repeat'),('link-v8-memory','link-v9-memory-repeat')]:
 x=runtime/first;y=runtime/second
 for path in x.iterdir():
  if not path.is_file() or (first.startswith('link') and not(path.suffix in ['.obj','.exe'] or path.name in ['linked-addresses.json','native-import-stops.json','validate.stdout'])):continue
  assert path.read_bytes()==(y/path.name).read_bytes(),(first,path.name);artifacts[first+'/'+path.name]=sha(path)
registry=read(runtime/'registry-v7-memory-repeat/summary.json');link=read(runtime/'link-v9-memory-repeat/summary.json');loader=read(runtime/'loader-plan-v8-memory/summary.json');assert registry['identity_sha256']==link['registry_identity_sha256']==loader['registry_identity_sha256'];assert link['linked_game_roots']==21282 and link['linked_import_gateways']==775 and link['tested_unimplemented_import_stops']==708 and not link['game_execution'];assert loader['unresolved_relocations']==37
for name,digest in loader['files'].items():assert sha(runtime/'loader-plan-v8-memory'/name)==sha(runtime/'loader-plan-v7-repeat'/name)==digest
for name in ['imports.json','targets.json','x87-sites.json','modules.json']:
 assert sha(runtime/'registry-v7-memory-repeat'/name)==sha(runtime/'registry-v5-service-identities'/name),name
records=[]
for suffix in ['native-memory-plan-v1','native-memory-compile-v1-preflight','native-memory-compile-v2-all','native-memory-compile-v3-repeat','native-memory-manifest-v1','memory-source-inspector-v2-fp-census','memory-source-checks-v1','control-origin-checks-v2-memory','control-exit-inventory-v11-memory','whole-program-linkage-v12-memory','coff-constants-v5-memory','source-exit-dispatch-v3-memory','native-registry-v6-memory','native-registry-v7-memory-repeat','native-link-v8-memory','native-link-v9-memory-repeat','native-loader-plan-v8-memory']:
 folder=ROOT/'local/runs'/('20260906-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,source_commit=record['project_commit'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
compiler=read(ROOT/'build/sparse-lift-v12-memory-sources/identity.json');inspector=read(ROOT/'build/control-audit-v8-memory-fp/identity.json');assert compiler['driver_source_sha256']==sha(ROOT/'native/sparse_lift/main.cpp');assert inspector['source_sha256']==sha(ROOT/'native/control_audit/main.cpp')
result=dict(status='whole startup source ABI migration, independent memory/control audit and repeated native linkage pass',migration=migration,inventory=inventory,registry=registry,link=link,loader=loader,compiler=compiler,inspector=inspector,bridged_ir_sites=sum(inventory['memory_source_counts'].values()),identical_artifacts=artifacts,recorders=records,game_execution=False,p4_gate_passed=False,limitations=['IR site counts describe semantic-inlined saved bitcode before clang O2; they are not execution coverage or final machine paths.','Unknown control targets, conditional recovery/export assumptions, missing target FP profile and fourteen unresolved x87 selector sites are unchanged.','This migration adds precise native memory faults, not guest exception delivery, private game loading or real services.','Native helper runtime cost remains unmeasured; object size grows from 67,835,213 to 74,174,245 bytes.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],bridged_ir_sites=result['bridged_ir_sites'],executable_sha256=link['executable_sha256'],executable_bytes=link['executable_bytes'])),flush=True)
