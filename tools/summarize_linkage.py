"""Publish the reproducible COFF inventory, constant checks and unresolved native gate."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike';current=base/'whole-program-linkage-v5-repeat';previous=base/'whole-program-linkage-v4-stubs'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
r=read(current/'summary.json');assert r['objects']==386 and r['compiled_roots']==21282 and r['unresolved_symbol_names']==240 and not r['unclassified_logical_targets']
assert r['unresolved_classes']=={'native support or host library symbol requires implementation/linkage':63,'import PLT requires native binding':177}
assert r['missing_start_context_counts']==dict(after_control_contract=4178,compiled_target_transfer=165,import_tail_transfer=23)
assert r['missing_instruction_start_records']==4366 and not r['emitted_ir_exit_sites_audited']
assert r['known_target_after_contract_records']==1
for name,digest in r['artifact_sha256'].items():assert sha(current/name)==digest==sha(previous/name)
objects=read(current/'objects.json');older=read(base/'whole-program-linkage-v2-context/objects.json');assert len(objects)==len(older)
for a,b in zip(objects,older,strict=True):
 assert {k:v for k,v in a.items() if k!='missing_blocks'}=={k:v for k,v in b.items() if k!='missing_blocks'}
 assert sha(current/f"object-{a['index']:04d}.nm.txt")==a['nm_sha256']==sha(previous/f"object-{a['index']:04d}.nm.txt")
constants=read(base/'coff-constants-v1/checked.json');assert constants['duplicate_symbols']==35 and constants['definitions']==90 and constants['objects']==12
for name,digest in constants['input_sha256'].items():assert sha(base/'whole-program-linkage-v2-context'/name)==digest
assert sha(current/'duplicate-definitions.json')==sha(base/'whole-program-linkage-v2-context/duplicate-definitions.json')
for c in constants['checks']:
 for o in c['occurrences']:assert sha(base/'coff-constants-v1'/f"object-{o['object']:04d}.readobj.txt")==o['readobj_sha256']
imports=[x for x in read(current/'unresolved-symbols.json') if x['kind'].startswith('import')];assert sum(len(x['bundled_candidates'])==1 for x in imports)==67 and sum(not x['bundled_candidates'] for x in imports)==110
assert all(c['compiled'] for x in imports for c in x['bundled_candidates'])
case=read(current/'known-target-after-contract.json');assert len(case)==1 and case[0]['rva']==0x210b730 and case[0]['preceding_control_contracts'][0]['source']==0x210b72b
runs={}
for suffix in ['whole-program-linkage-v2-context','whole-program-linkage-v3-import-tail','whole-program-linkage-v4-stubs','whole-program-linkage-v5-repeat','coff-constants-v1']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for file,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(file.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
evidence=dict(status='complete current COFF symbol census and missing-start contexts verified; native exit handling remains open',inventory=r,constant_check=constants,known_target_after_contract=case,runs=runs,retained_failures=['20260906-p3-whole-program-linkage-v1 rejected an input-format assumption: units.json has identities, not full instructions. V2 reads current manifests once and verifies every retained entry instruction hash.'],
next_work=['Inspect actual emitted LLVM control exits, including dynamic unexpected-return guards absent from the missing-instruction-start list.','Preserve source and exit intent in the native interface; never dispatch an unexpected return just because its address is compiled.','Bind 67 supplied compiled export candidates through verified module/relocation contracts; implement or diagnose the 110 external import stubs and 63 support/library symbols explicitly.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/linkage-evidence.json',evidence);write_json(out/'summary.json',dict(status=evidence['status'],objects=386,compiled_roots=21282,unresolved_symbols=240,import_stubs=177,support_symbols=63,duplicate_constants=35,missing_instruction_start_records=4366,emitted_ir_exit_sites_audited=False));print(json.dumps(read(out/'summary.json')),flush=True)
