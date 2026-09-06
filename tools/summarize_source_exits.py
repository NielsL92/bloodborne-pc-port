"""Check source-exit/compiler repeats, LLVM/COFF audits and independent tail stubs."""
import argparse,collections,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
manifest=read(base/'source-exit-manifest-v2-regression/evidence.json');inventory=read(base/'control-exit-inventory-v10-source-repeat/summary.json');linkage=read(base/'whole-program-linkage-v11-source-repeat/summary.json');dispatch=read(base/'source-exit-dispatch-v2-tail-imports/summary.json');constants=read(base/'coff-constants-v4-source-exits/checked.json')
active_hash=manifest['active_manifest_sha256'];assert active_hash==inventory['active_manifest_sha256']==linkage['active_manifest_sha256']==dispatch['active_manifest_sha256'];assert inventory['site_counts'].get('__remill_missing_block',0)==0 and inventory['site_counts'].get('__remill_error',0)==0;assert inventory['cfg_reachable_site_counts']['__bb_native_block_transfer']==552 and inventory['cfg_unreachable_site_counts']['__bb_native_block_transfer']==4261
for before,after in [('control-exit-inventory-v9-source-exits','control-exit-inventory-v10-source-repeat'),('whole-program-linkage-v10-source-exits','whole-program-linkage-v11-source-repeat')]:
 one=read(base/before/'summary.json');two=read(base/after/'summary.json');assert one==two
 for name,digest in two['artifact_sha256'].items():assert sha(base/before/name)==sha(base/after/name)==digest
 for n in range(386):
  name=f'object-{n:04d}.json' if before.startswith('control') else f'object-{n:04d}.nm.txt';assert sha(base/before/name)==sha(base/after/name)
for name in ['objects.json','contracts.json','identity.json','summary.json']:assert sha(base/'source-exit-plan-v1'/name)==sha(base/'source-exit-plan-v2-repeat'/name)
for row in read(base/'source-exit-plan-v1/objects.json'):
 for name in ['input.json','roots.json','units.json']:assert sha(base/'source-exit-plan-v1'/row['prepared_folder']/name)==sha(base/'source-exit-plan-v2-repeat'/row['prepared_folder']/name)
assert dispatch['unique_pairs']==551 and dispatch['target_classes']=={'compiled root':524,'verified import stub':27};assert dispatch['runtime_import_stubs']==182 and len(dispatch['tail_only_import_stubs'])==5
raw=Path('local/cfg/ghidra-tail-imports-v1');ghidra=read(raw/'summary.json');assert ghidra['windows']==5 and ghidra['instructions']==5;wanted={(r['module'],r['rva']):r for r in dispatch['tail_only_import_stubs']};checked=[]
for module in ghidra['modules']:
 path=raw/module['name']/'ghidra.json';assert sha(path)==module['raw_sha256']
 for window in read(path):
  row=wanted[module['module'],window['start']];assert len(window['instructions'])==1;ins=window['instructions'][0];assert ins['rva']==row['rva'] and ins['bytes']==row['stub_bytes'] and ins['length']==6;checked.append(dict(module=row['module'],rva=row['rva'],instruction=ins,relocation=row['relocation'],symbol=row['symbol_record']))
assert len(checked)==5;origins=read(base/'control-origin-checks-v1/summary.json');assert origins['synthetic_cases']==4 and origins['authored_transfer_sites']==6
# Compare the actual compiler bytes, not just retained unit hash labels.
recovered={}
for line in Path('local/cfg/startup-recovery-v31-conditional-repeat/compilation-manifest.jsonl').open(encoding='utf-8'):
 unit=json.loads(line)
 for ins in unit['instructions']:
  key=unit['module_sha256'],ins['rva']
  if key in recovered:assert recovered[key]==ins['bytes']
  recovered[key]=ins['bytes']
bases={m['module']:m['logical_base'] for m in manifest['identity']['module_mapping']};seen=collections.Counter()
for obj in read(base/'source-exit-manifest-v2-regression/active-objects.json'):
 data=read(base/obj['source_batch']/obj['folder']/'input.json')
 for ins in data['instructions']:
  key=obj['module'],ins['address']-bases[obj['module']];assert recovered[key]==ins['bytes'];seen[key]+=1
assert set(seen)==set(recovered) and len(seen)==874279 and set(seen.values())=={1}
reachable_nonreturn={int(r['arguments'][1]['value_hex'],16) for r in read(base/'control-exit-inventory-v10-source-repeat/sourced-control-sites.json') if r['callee']=='__bb_native_control_fault' and r['cfg_reachable_from_entry'] and r['arguments'][3]['value_hex']=='2'}
evidence=dict(status='repeated whole-set source-aware compilation and exit registry verified; native binding/linkage gate remains open',compilation=manifest,llvm=inventory,coff=linkage,constants=constants,dispatch=dispatch,ghidra_tail_stubs=checked,origin_checks=origins,unique_cfg_reachable_nonreturn_sources=len(reachable_nonreturn),actual_instruction_bytes_checked=len(seen),retained_failures=['source-exit-checks-v1 lacked the authored TEST undefined-AF binding; v2/v3 pass with undefined AF excluded.','source-exit-manifest-v1 incorrectly expected pre-O2 IR to stay identical after source-slot stores; corrected v2 verifies the unchanged native ordinary-call object/outcome and exact complete-set repeats.','source-exit-dispatch-v1 retained five unresolved targets outside the COFF symbol list. Existing raw PLT relocation evidence plus new independent Ghidra windows resolve these five tail-only import identities.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(a.out/'checked.json',evidence);write_json(Path('reports/source-exits-evidence.json'),evidence);write_json(Path('reports/control-exits-evidence.json'),dict(status=evidence['status'],inventory=inventory,dispatch=dispatch,source_evidence='reports/source-exits-evidence.json',p3_gate_passed=False));write_json(Path('reports/linkage-evidence.json'),dict(status=evidence['status'],inventory=linkage,constants=constants,runtime_import_stubs=182,tail_only_import_stubs=checked,source_evidence='reports/source-exits-evidence.json',p3_gate_passed=False));print(json.dumps(dict(status=evidence['status'],active_manifest_sha256=active_hash,unique_source_target_pairs=551,runtime_import_stubs=182,unique_cfg_reachable_nonreturn_sources=len(reachable_nonreturn))),flush=True)
