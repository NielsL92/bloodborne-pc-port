"""Audit exact conditional ending changes and the complete static compilation census."""
import collections,hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.conditional_control_inventory import SITES
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);cfg=root/'local/cfg';base=root/'local/compiler-spike';source=cfg/'startup-recovery-v31-conditional-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
proof=read(cfg/'conditional-control-checked-v1/checked.json');assert proof['status']=='independent conditional callback-control comparison passed' and proof['shared_instructions']==650
for p,digest in proof['evidence'].items():assert sha(p)==digest
repro={}
for name in ['analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json']:
 digest=sha(source/name);assert digest==sha(cfg/'startup-recovery-v30-conditional-control'/name);repro['recovery/'+name]=digest
assert read(source/'identity.json')['conditional_control_evidence_sha256']==sha(cfg/'conditional-control-checked-v1/checked.json')
delta=read(cfg/'conditional-control-delta-v1/delta.json');assert delta['target_db_sha256']==repro['recovery/analysis.sqlite'] and delta['target_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert delta['units']==21181 and len(delta['changed'])==5 and delta['remaining_quarantines']==0
old=read(base/'conditional-control-compile-v1/results.json');new=read(base/'conditional-control-compile-v2-repeat/results.json');assert len(old)==len(new)==2
expected={(h,e) for h,e,pc,t in SITES};compiled=set()
for x,y in zip(old,new,strict=True):
 assert x['status']==y['status']=='object_built' and x['module']==y['module'] and x['entries']==y['entries']
 compiled.update((y['module'],e) for e in y['entries'])
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:
  p=base/'conditional-control-compile-v1'/x['folder']/name;q=base/'conditional-control-compile-v2-repeat'/y['folder']/name;assert sha(p)==sha(q);repro[y['folder']+'/'+name]=sha(q)
assert compiled==expected and sum(y['instructions'] for y in new)==540
ci=read(base/'conditional-control-compile-v2-repeat/identity.json');assert ci['source_db_sha256']==repro['recovery/analysis.sqlite'] and ci['source_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert ci['lifter_sha256']==sha(root/'build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe') and ci['semantics_sha256']==sha(root/'build/extended-semantics-v31-scale/amd64_avx.bc')
previous=base/'lua-panic-evidence-audit-v1/active-objects.json';assert sha(previous)=='d6dfcad6be850c130aed3c9d0fa91512fa7051426c0c95bddebd340a42f0fbc3';active=read(previous);assert len(active)==384
for y in new:active.append({k:y[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}|dict(source_batch='conditional-control-compile-v2-repeat'))
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(instruction_set_sha256=u['instruction_set_sha256'],issues=u['issues'],constructor_ordinal=u['constructor_ordinal'])
entries=collections.Counter();roots=collections.Counter()
for obj in active:
 p=base/obj['source_batch']/obj['folder'];assert sha(p/'function.obj')==obj['object_sha256'];units=read(p/'units.json');assert {u['entry'] for u in units}==set(obj['entries'])
 for u in units:
  key=obj['module'],u['entry'];assert current[key]['instruction_set_sha256']==u['instruction_set_sha256'];entries[key]+=1
 roots.update(obj['compiled_roots'])
assert len(active)==386 and len(entries)==21181 and set(entries.values())==set(roots.values())=={1} and set(entries)==set(current)
# Audit all seven explicit missing-block exits in the newly compiled cohort.
# Five are unexpected returns from these conditional endings; one is a prior
# stack-protector terminal and one is a known cross-unit tail transfer.
from tools.startup_service_inventory import MAIN,LIBC
expected_missing={LIBC:{0x60546,0x605de,0x60747},MAIN:{0x210b722,0x210b730,0x210b9e5,0x210d390}};exit_classifications=[]
for obj in new:
 h=obj['module'];logical_base=0x800000000 if h==LIBC else 0x100000000
 actual={pc-logical_base for pc in obj['missing_instruction_starts']};assert actual==expected_missing[h]
 for pc in sorted(actual):
  if h==MAIN and pc==0x210d390:
   assert entries[h,pc]==1
   assert any(u['module_sha256']==h and u['entry']==0x210b940 and any(e['kind']=='cross_fence_jump' and e['target']==pc for e in u['edges']) for u in proof['units'])
   category='known compiled cross-unit tail transfer; native dispatcher required'
  elif h==MAIN and pc==0x210b722:
   assert any(u['module_sha256']==h and any(e['source']==pc-5 and e['kind']=='annotated_control_contract_requires_runtime' and e['detail']=='stack-protector-failure' for e in u['edges']) for u in proof['units'])
   category='unexpected return from existing stack-protector contract'
  else:
   assert any(m==h and site+5==pc for m,entry,site,target in SITES)
   category='unexpected return from new conditional ending contract'
  exit_classifications.append(dict(module=h,rva=pc,kind=category,native_handler_validated=False))
assert len(exit_classifications)==7
assert not any(u['issues'] for u in current.values());constructors=sum(current[k]['constructor_ordinal'] is not None for k in entries);assert constructors==18444
summary=read(source/'summary.json');assert summary['counts']['recovery_entry']==21181 and summary['counts']['recovery_instruction']==874279 and summary['counts']['recovery_issue']==0
for k,v in dict(unresolved_indirect_call=9044,unresolved_indirect_jump=430,unresolved_callback_argument=143,unresolved_native_service_control=3,unresolved_conditional_control_continuation=5,initial_symbol_dispatch_target_candidate=1,symbol_dispatch_binding_unvalidated=1,stored_lua_panic_target_candidate=2,lua_panic_binding_unvalidated=2).items():assert summary['frontier_counts'][k]==v
runs={}
for suffix in ['conditional-control-inventory-v2-edges','ghidra-conditional-control-v1','conditional-control-checked-v1','conditional-control-checks-v1','startup-recovery-v30-conditional-control','startup-recovery-v31-conditional-repeat','conditional-control-delta-v1','conditional-control-compile-v1','conditional-control-compile-v2-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
checks=(root/'local/runs/20260906-p3-conditional-control-checks-v1/stderr.log').read_text(encoding='utf-8');assert 'Ran 88 tests' in checks and checks.rstrip().endswith('OK')
write_json(out/'active-objects.json',active);write_json(out/'quarantined.json',[])
r=dict(status='all current manifest entries compile under explicit boundary conditions; P3 execution-exit handling remains open',source=source.relative_to(root).as_posix(),proof=proof,recovery_delta=delta,recovery=summary,active_objects_manifest=(out.relative_to(root)/'active-objects.json').as_posix(),active_objects_sha256=sha(out/'active-objects.json'),previous_active_objects_manifest=previous.relative_to(root).as_posix(),previous_active_objects_sha256=sha(previous),compiled_entries=len(entries),compiled_objects=len(active),compiled_constructors=constructors,remaining_compiler_rejections=0,remaining_quarantines=[],new_compile=new,new_explicit_exits=exit_classifications,reproducible_artifacts=repro,runs=runs,
 retained_failures=['20260906-p3-conditional-control-inventory-v1 rejected absent fallthrough edges: compilation manifests intentionally omit them. V2 loads indexed recovery_edge rows, verifies its nonfallthrough subset equals the manifest, and retains all ordinary-flow evidence. Both libc indirect calls independently use RCX, not an assumed RAX.'],
 limitations=['The five disputed endings are conditionally compilable, not proved native transfers. Three exact unknown callback CALL sites require ordinary return or explicit nonlocal/termination behavior. Those unknown calls and all candidate/mutation assumptions remain.','Only five module/entry/call sites receive annotations; generic unknown-call rejection and all other call sites are unchanged. Base ABI contracts are verified directly; no old derived summary is silently imported.','Every decoded instruction, original unknown-target count and initial constructor remains unchanged. The five native continuation obligations remain explicit and P3 does not pass merely from zero compiler rejections/quarantines.','The complete object set has not been linked or executed. Linkage, native import/return/callback/exception handling and unknown-target diagnostics still need a gate audit. No native game boot or new P1 observation.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/conditional-control-evidence.json',r);compact={k:r[k] for k in ['status','source','compiled_entries','compiled_objects','compiled_constructors','remaining_compiler_rejections','active_objects_manifest','active_objects_sha256']};compact['remaining_quarantines']=0;write_json(out/'summary.json',compact);print(json.dumps(compact),flush=True)
