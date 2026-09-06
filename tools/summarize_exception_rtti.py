"""Audit the initial RTTI candidate, exact recovery delta and complete active object set."""
import collections,hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import LIBC
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);cfg=root/'local/cfg';base=root/'local/compiler-spike';source=cfg/'startup-recovery-v27-rtti-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
proof=read(cfg/'exception-rtti-checked-v2-provenance/checked.json');assert proof['status']=='independent RTTI symbol-dispatch candidate passed' and proof['shared_instructions']==100
for p,digest in proof['evidence'].items():assert sha(p)==digest
for table in proof['raw_tables'].values():assert sha(table['path'])==table['sha256']
repro={}
for name in ['analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json']:
 digest=sha(source/name);assert digest==sha(cfg/'startup-recovery-v26-rtti'/name);repro['recovery/'+name]=digest
identity=read(source/'identity.json');assert identity['symbol_dispatch_evidence_sha256']==sha(cfg/'exception-rtti-checked-v2-provenance/checked.json')
delta=read(cfg/'exception-rtti-delta-v1/delta.json');assert delta['target_db_sha256']==repro['recovery/analysis.sqlite'] and delta['target_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert delta['unchanged_entries']==21177 and len(delta['added'])==len(delta['changed'])==1
old=read(base/'exception-rtti-compile-v1/results.json');new=read(base/'exception-rtti-compile-v2-repeat/results.json');assert len(old)==len(new)==1
x,y=old[0],new[0];assert x['status']==y['status']=='object_built' and x['entries']==y['entries']==[0x48f00] and y['module']==LIBC
assert y['instructions']==4 and y['roots']==1 and y['object_bytes']==1228 and not y['missing_instruction_starts']
for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:
 p=base/'exception-rtti-compile-v1'/x['folder']/name;q=base/'exception-rtti-compile-v2-repeat'/y['folder']/name;assert sha(p)==sha(q);repro['compile/'+name]=sha(q)
ci=read(base/'exception-rtti-compile-v2-repeat/identity.json');assert ci['source_db_sha256']==repro['recovery/analysis.sqlite'] and ci['source_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert ci['lifter_sha256']==sha(root/'build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe') and ci['semantics_sha256']==sha(root/'build/extended-semantics-v31-scale/amd64_avx.bc')
previous=base/'startup-services-evidence-audit-v1/active-objects.json';assert sha(previous)=='cd619f4a781c67cf3e0b091387e5473ba0d2867e3595d6c0c516c8e02f2b87ea';active=read(previous);assert len(active)==382
active.append({k:y[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}|dict(source_batch='exception-rtti-compile-v2-repeat'))
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(instruction_set_sha256=u['instruction_set_sha256'],issues=u['issues'],constructor_ordinal=u['constructor_ordinal'])
entries=collections.Counter();roots=collections.Counter()
for obj in active:
 p=base/obj['source_batch']/obj['folder'];assert sha(p/'function.obj')==obj['object_sha256'];units=read(p/'units.json');assert {u['entry'] for u in units}==set(obj['entries'])
 for u in units:
  key=(obj['module'],u['entry']);assert current[key]['instruction_set_sha256']==u['instruction_set_sha256'];entries[key]+=1
 roots.update(obj['compiled_roots'])
assert len(active)==383 and len(entries)==21174 and set(entries.values())==set(roots.values())=={1}
assert set(entries)=={k for k,v in current.items() if not v['issues']}
constructors=sum(current[k]['constructor_ordinal'] is not None for k in entries);assert constructors==18444
quarantines=[dict(module=k[0],entry=k[1],issues=v['issues']) for k,v in current.items() if v['issues']];assert len(quarantines)==5
summary=read(source/'summary.json');assert summary['counts']['recovery_entry']==21179 and summary['counts']['recovery_instruction']==874269
for k,v in dict(unresolved_indirect_call=9044,unresolved_indirect_jump=430,unresolved_callback_argument=143,unresolved_native_service_control=3,fallthrough_at_fence=5,initial_symbol_dispatch_target_candidate=1,symbol_dispatch_binding_unvalidated=1).items():assert summary['frontier_counts'][k]==v
runs={}
for suffix in ['exception-rtti-inventory-v1','ghidra-rtti-symbols-v1','ghidra-rtti-windows-v1','exception-rtti-checked-v1','exception-rtti-checked-v2-provenance','symbol-dispatch-checks-v1','startup-recovery-v26-rtti','startup-recovery-v27-rtti-repeat','exception-rtti-delta-v1','exception-rtti-compile-v1','exception-rtti-compile-v2-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
checks=(root/'local/runs/20260906-p3-symbol-dispatch-checks-v1/stderr.log').read_text(encoding='utf-8');assert 'Ran 65 tests' in checks and checks.rstrip().endswith('OK')
write_json(out/'active-objects.json',active);write_json(out/'quarantined.json',quarantines)
r=dict(status='one independently checked initial RTTI candidate recovered and compiled; P3 remains open',source=source.relative_to(root).as_posix(),proof=proof,recovery_delta=delta,recovery=summary,active_objects_manifest=(out.relative_to(root)/'active-objects.json').as_posix(),active_objects_sha256=sha(out/'active-objects.json'),previous_active_objects_manifest=previous.relative_to(root).as_posix(),previous_active_objects_sha256=sha(previous),compiled_entries=len(entries),compiled_objects=len(active),compiled_constructors=constructors,remaining_compiler_rejections=0,remaining_quarantines=quarantines,new_compile=y,reproducible_artifacts=repro,runs=runs,
 limitations=['Both symbol-based relocations and the 10-byte target body are independently checked. They establish one initial candidate, not an immutable runtime target.','The original indirect call at libc 0x60811 and subsequent object call at 0x6081f remain unresolved. The new binding obligation retains symbol interposition, object/table writes and runtime identity.','The four-instruction object has no sparse missing paths but still requires native memory/return dispatch and arithmetic flag support. Object compilation is not game execution.','All prior entry instruction hashes and unique compiled-root ownership remain valid. Five quarantines, all initial constructor mutation assumptions and all existing unknown-target counts remain unchanged.','No native game boot, playable port, P3 pass, P4 startup, or P1 observation is established by this static extension.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/exception-rtti-evidence.json',r);compact={k:r[k] for k in ['status','source','compiled_entries','compiled_objects','compiled_constructors','remaining_compiler_rejections','active_objects_manifest','active_objects_sha256']};compact['remaining_quarantines']=len(quarantines);write_json(out/'summary.json',compact);print(json.dumps(compact),flush=True)
