"""Audit exact selectors, whole-object replacement and the static startup census."""
import collections,hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike';source=root/'local/cfg/startup-recovery-v22-cache-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
inventory=read(base/'x87-selector-inventory-v1/summary.json');sites=read(base/'x87-selector-inventory-v1/sites.json');plan=read(base/'x87-replacement-plan-v1/summary.json');replaced=read(base/'x87-replacement-plan-v1/replaced-objects.json');retained=read(base/'x87-replacement-plan-v1/retained-objects.json');selected={(r['module'],r['start']) for r in read(base/'x87-replacement-plan-v1/entries.json')}
assert inventory['sites']==len(sites)==360 and inventory['problem_count']==0 and inventory['x87_sites']==355 and inventory['mxcsr_sites']==5 and inventory['owners']==12
assert plan['prior_entries']==21168 and plan['replaced_objects']==5 and plan['replacement_entries']==65 and not plan['stale_instruction_sets'] and not plan['prior_logical_root_duplicates']
current={};selected_units={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);key=(u['module_sha256'],u['entry']);current[key]=dict(instruction_set_sha256=u['instruction_set_sha256'],issues=u['issues'],constructor_ordinal=u['constructor_ordinal'])
 if key in selected:selected_units[key]=u
sem=root/'build/extended-semantics-v31-scale';identity=read(sem/'identity.json');driver=root/'build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe';driver_identity=read(driver.parent/'identity.json')
assert sha(driver)==driver_identity['executable_sha256']==inventory['lifter_sha256'] and sha(root/'native/sparse_lift/main.cpp')==driver_identity['driver_source_sha256']
assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']==inventory['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in identity['authored_header_sha256'].items():assert sha(root/path)==digest
repro={}
for first,second,expected in [('x87-integration-compile-v1','x87-integration-compile-v2-repeat',12),('x87-replacement-compile-v1','x87-replacement-compile-v2-repeat',65)]:
 a=base/first;b=base/second;ra=read(a/'results.json');rb=read(b/'results.json');assert len(ra)==len(rb) and sum(len(r['entries']) for r in rb)==expected
 for x,y in zip(ra,rb):
  assert x['entries']==y['entries'] and x['module']==y['module'] and x['status']==y['status']=='object_built'
  for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:
   p=a/x['folder']/name;q=b/y['folder']/name;assert p.read_bytes()==q.read_bytes();repro[second+'/'+y['folder']+'/'+name]=sha(q)
# Adding audit fields must not change AOT results or generated numeric/function code.
for name in ['function.bc','function.obj','numeric.obj','execute.stdout']:
 a=base/'x87-scale-bindings-v2-repeat'/name;b=base/'x87-scale-bindings-v3-selector-audit'/name;assert a.read_bytes()==b.read_bytes();repro['selector-audit-unchanged/'+name]=sha(b)
newdir=base/'x87-replacement-compile-v2-repeat';results=read(newdir/'results.json');assert len(results)==1;r=results[0];artifact=newdir/r['folder'];newidentity=read(newdir/'identity.json');bases={x['module']:x['logical_base'] for x in newidentity['module_mapping']}
assert r['instructions']==4766 and r['roots']==65 and r['object_bytes']==981385 and r['object_sha256']==sha(artifact/'function.obj')
actual_selectors={x['address']:x for x in read(artifact/'audit.json')['decoded_selectors']}
for site in sites:
 actual=actual_selectors[bases[site['module']]+site['rva']];assert actual['lifted'] and actual['selector']==site['selector'] and actual['implementation']==site['implementation'] and site['authored_binding']['implementation'] in actual['implementation']
ir=(artifact/'function.ll').read_text(encoding='utf-8');assert '__remill_fpu_' not in ir and 'x86_fp80' not in ir
active=[dict(source_batch=x['source_batch'],folder=x['folder'],module=x['module'],entries=x['entries'],compiled_roots=x['compiled_roots'],object_sha256=x['object_sha256'],object_bytes=x['object_bytes']) for x in retained]
active.append(dict(source_batch='x87-replacement-compile-v2-repeat',folder=r['folder'],module=r['module'],entries=r['entries'],compiled_roots=r['compiled_roots'],object_sha256=r['object_sha256'],object_bytes=r['object_bytes']))
entry_owners=collections.defaultdict(list);root_owners=collections.defaultdict(list)
for obj in active:
 p=base/obj['source_batch']/obj['folder'];assert sha(p/'function.obj')==obj['object_sha256']
 for u in read(p/'units.json'):
  key=(obj['module'],u['entry']);assert current[key]['instruction_set_sha256']==u['instruction_set_sha256'];entry_owners[key].append(obj['source_batch']+'/'+obj['folder'])
 for pc in obj['compiled_roots']:root_owners[pc].append(obj['source_batch']+'/'+obj['folder'])
assert len(active)==380 and len(entry_owners)==21170 and all(len(v)==1 for v in entry_owners.values()) and all(len(v)==1 for v in root_owners.values())
assert set(entry_owners)=={key for key,v in current.items() if not v['issues']};constructors=sum(current[key]['constructor_ordinal'] is not None for key in entry_owners);assert constructors==18444
quarantined=[dict(module=key[0],entry=key[1],issues=v['issues']) for key,v in current.items() if v['issues']];assert len(quarantined)==8
boundaries=[]
for pc in r['missing_instruction_starts']:
 rva=pc-bases[r['module']];sources=[];direct=[]
 for (module,entry),u in selected_units.items():
  if module!=r['module']:continue
  for ins in u['instructions']:
   if ins['rva']+ins['size']==rva:sources.append(dict(entry=entry,instruction=ins,edges=[e for e in u['edges'] if e['source']==ins['rva']]))
  direct.extend(dict(entry=entry,edge=e) for e in u['edges'] if e['target_module']==module and e['target']==rva)
 classified=any(e['kind']=='annotated_control_contract_requires_runtime' and e['detail']=='stack-protector-failure' for s in sources for e in s['edges'])
 import_edges=[x for x in direct if x['edge']['kind']=='import_contract_unvalidated']
 boundaries.append(dict(module=r['module'],rva=rva,kind='unexpected-return-after-stack-protector-failure' if classified else 'import-endpoint' if import_edges else 'explicit-unclassified-boundary',preceding=sources,incoming=direct))
assert len(boundaries)==17;write_json(out/'boundaries.json',boundaries);write_json(out/'active-objects.json',active);write_json(out/'quarantined.json',quarantined)
checks={}
for name in ['sparse-checks-v8-selector-audit','sparse-mmx-checks-v2-selector-audit','x87-opcode-checks-v3-selector-audit','sparse-trap-checks-v3-selector-audit','x87-scale-bindings-v3-selector-audit']:checks[name]=read(base/name/'summary.json')
assert checks['x87-scale-bindings-v3-selector-audit']['cases']==2809856 and checks['x87-scale-bindings-v3-selector-audit']['differing_cases']==0
assert checks['sparse-mmx-checks-v2-selector-audit']['rejected_mmx']==12 and checks['sparse-mmx-checks-v2-selector-audit']['accepted_controls']==3 and checks['x87-opcode-checks-v3-selector-audit']['cases']==112
runs={}
for suffix in ['sparse-lift-v8-selector-audit','x87-selector-inventory-v1','x87-integration-compile-v1','x87-integration-compile-v2-repeat','sparse-checks-v8-selector-audit','x87-scale-bindings-v3-selector-audit','sparse-mmx-checks-v2-selector-audit','x87-opcode-checks-v3-selector-audit','sparse-trap-checks-v3-selector-audit','x87-replacement-plan-v1','x87-replacement-compile-v1','x87-replacement-compile-v2-repeat','x87-integration-evidence-audit-v1']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix=='x87-integration-evidence-audit-v1' else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'ValueError' in (root/'local/runs/20260906-p3-x87-integration-evidence-audit-v1/stderr.log').read_text(encoding='utf-8')
report=dict(retained_failure='Audit v1 completed its checks but failed writing the report artifact reference because a relative output path was compared with the absolute workspace path. V2 resolves the output path first; the failed source snapshot and partial local outputs remain preserved.',status='static x87 integration and whole-object replacement pass; P3 control closure remains open',inventory=inventory,replacement_plan=plan,replacement_compile=read(newdir/'summary.json'),replacement_instructions=r['instructions'],runtime_declarations=r['external_declarations'],boundaries=boundaries,boundary_kinds=dict(collections.Counter(x['kind'] for x in boundaries)),active_objects_manifest=out.relative_to(root).as_posix()+'/active-objects.json',active_objects_sha256=sha(out/'active-objects.json'),compiled_entries=len(entry_owners),compiled_objects=len(active),compiled_constructors=constructors,remaining_compiler_rejections=0,remaining_quarantined_entries=8,quarantined=quarantined,reproducible_artifacts=repro,checks=checks,runs=runs,source_sha256={x:sha(root/x) for x in ['native/sparse_lift/main.cpp','tools/x87_selector_inventory.py','tools/x87_replacement_plan.py']},semantics='v31-scale for the new replacement object; retained objects keep their recorded semantics',compiler='v8-selector-audit for the replacement object; retained objects keep their recorded compilers',limitations=['This accepts the new object for the static compilation census, not game execution or native runtime correctness.','Five prior objects containing 63 entries are replaced as complete objects by one reproducible 65-entry object. Old files remain intact. The 12 one-entry objects are diagnostic experiments and are excluded from the active set.','Every active entry instruction-set hash matches the canonical current manifest; every entry and compiled logical root has one owner. The active set contains every issue-free manifest and all initial constructors.','All 355 recovered x87 sites and five MXCSR sites select their checked authored bindings. No legacy Remill FPU helper or x86_fp80 IR remains in the exact catalog or new complete object.','Eight fallthrough-at-fence quarantines remain outside compilation. Unknown indirect/callback targets, constructor mutability and import/nonlocal/exception contracts remain visible and unresolved.','The new object retains 17 explicit missing-path records and 89 runtime/compiled-target declarations. Native import dispatch, stack-protector failure, floating-state profiles and exception delivery still need implementations.','Intel hardware characterizations, comparison/image policies and pointer limits remain as recorded in the x87 reports. No AMD Jaguar execution equivalence, performance improvement, native game boot or playable port is claimed.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-integration-evidence.json',report);summary={k:report[k] for k in ['status','compiled_entries','compiled_objects','compiled_constructors','remaining_compiler_rejections','remaining_quarantined_entries','boundary_kinds','active_objects_manifest','active_objects_sha256']};write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
