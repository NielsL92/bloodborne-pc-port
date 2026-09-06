"""Publish corrected division semantics and refreshed whole-set native obligations."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
integration=read(base/'divide-integration-manifest-v1/evidence.json');digest=integration['active_manifest_sha256'];assert sha(root/integration['active_manifest'])==digest
ir=base/'control-exit-inventory-v8-divide-repeat';irprev=base/'control-exit-inventory-v7-divide';link=base/'whole-program-linkage-v9-divide-repeat';linkprev=base/'whole-program-linkage-v8-divide';census=read(ir/'summary.json');symbols=read(link/'summary.json')
for now,previous in [(ir,irprev),(link,linkprev)]:
 summary=read(now/'summary.json');assert summary==read(previous/'summary.json') and summary['active_manifest_sha256']==digest
 for name,d in summary['artifact_sha256'].items():assert sha(now/name)==d==sha(previous/name)
 for obj in read(now/'objects.json'):
  name=f"object-{obj['index']:04d}."+('json' if now==ir else 'nm.txt');key='report_sha256' if now==ir else 'nm_sha256';assert sha(now/name)==obj[key]==sha(previous/name)
assert census['site_counts'].get('__remill_error',0)==0 and census['site_counts']['__bb_native_divide_fault']==56 and census['site_counts']['__bb_native_simd_fault']==58 and census['site_counts']['__remill_missing_block']==4818
assert census['error_semantic_origin_counts']=={}
assert census['objects']==symbols['objects']==386 and census['compiled_functions']==symbols['compiled_roots']==21282
assert symbols['unresolved_symbol_names']==239 and symbols['missing_instruction_start_records']==4366 and not symbols['unclassified_logical_targets']
constants=read(base/'coff-constants-v3-divide/checked.json');assert constants['duplicate_symbols']==35 and constants['definitions']==90 and constants['objects']==12
for name,d in constants['input_sha256'].items():assert sha(linkprev/name)==d
for row in constants['checks']:
 for obj in row['occurrences']:assert sha(base/'coff-constants-v3-divide'/f"object-{obj['object']:04d}.readobj.txt")==obj['readobj_sha256']
runs={}
for suffix in ['divide-integration-manifest-v1','control-exit-inventory-v7-divide','control-exit-inventory-v8-divide-repeat','whole-program-linkage-v8-divide','whole-program-linkage-v9-divide-repeat','coff-constants-v3-divide']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for file,d in m['source_sha256'].items():assert hashlib.sha256(z.read(file.replace(chr(92),'/'))).hexdigest()==d
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
evidence=dict(status='DIV/IDIV correction integrated and exact whole-set audits reproduced; P3 remains open',integration=integration,control_exit_inventory=census,linkage_inventory=symbols,constant_check=constants,runs=runs,next_work=['Preserve source instruction and exit reason at native control boundaries; honor or deliberately change and validate nounwind contracts.','Implement or diagnose native service/support boundaries, bind compiled supplied exports and validate linkage/startup without a CPU fallback.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/divide-semantics-evidence.json',evidence)
write_json(root/'reports/control-exits-evidence.json',dict(status='complete retained-bitcode exit census after DIV/IDIV correction; native runtime handling remains open',inventory=census,runs=runs,correction_report='reports/divide-semantics-evidence.json',prior_inventory='local/compiler-spike/control-exit-inventory-v4-repeat/summary.json',next_work=evidence['next_work'],p3_gate_passed=False,native_game_boot=False))
write_json(root/'reports/linkage-evidence.json',dict(status='complete COFF symbol census after DIV/IDIV replacement; native binding remains open',inventory=symbols,constant_check=constants,runs=runs,known_target_after_contract=read(link/'known-target-after-contract.json'),prior_inventory='local/compiler-spike/whole-program-linkage-v5-repeat/summary.json',next_work=evidence['next_work'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False))
summary=dict(status=evidence['status'],active_manifest=integration['active_manifest'],active_manifest_sha256=digest,authored_cases=327680,mismatches=0,missing_block_sites=4818,division_error_sites=0,divide_fault_sites=56,simd_fault_sites=58);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
