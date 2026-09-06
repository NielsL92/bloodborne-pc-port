"""Audit the stored Lua panic candidates, exact recovery delta and complete active object set."""
import collections,hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import MAIN
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);cfg=root/'local/cfg';base=root/'local/compiler-spike';source=cfg/'startup-recovery-v29-lua-panic-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
proof=read(cfg/'lua-panic-checked-v1/checked.json');assert proof['status']=='independent Lua panic field candidates passed' and proof['shared_instructions']==813
for p,digest in proof['evidence'].items():assert sha(p)==digest
repro={}
for name in ['analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json']:
 digest=sha(source/name);assert digest==sha(cfg/'startup-recovery-v28-lua-panic'/name);repro['recovery/'+name]=digest
identity=read(source/'identity.json');assert identity['lua_panic_evidence_sha256']==sha(cfg/'lua-panic-checked-v1/checked.json')
delta=read(cfg/'lua-panic-delta-v1/delta.json');assert delta['target_db_sha256']==repro['recovery/analysis.sqlite'] and delta['target_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert delta['unchanged_entries']==21178 and len(delta['added'])==2 and len(delta['changed'])==1
old=read(base/'lua-panic-compile-v1/results.json');new=read(base/'lua-panic-compile-v2-repeat/results.json');assert len(old)==len(new)==1
x,y=old[0],new[0];assert x['status']==y['status']=='object_built' and x['entries']==y['entries']==[0x2100e00,0x21155e0] and y['module']==MAIN
assert y['instructions']==10 and y['roots']>=2 and y['object_bytes']>0
for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:
 p=base/'lua-panic-compile-v1'/x['folder']/name;q=base/'lua-panic-compile-v2-repeat'/y['folder']/name;assert sha(p)==sha(q);repro['compile/'+name]=sha(q)
ci=read(base/'lua-panic-compile-v2-repeat/identity.json');assert ci['source_db_sha256']==repro['recovery/analysis.sqlite'] and ci['source_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert ci['lifter_sha256']==sha(root/'build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe') and ci['semantics_sha256']==sha(root/'build/extended-semantics-v31-scale/amd64_avx.bc')
previous=base/'exception-rtti-evidence-audit-v1/active-objects.json';assert sha(previous)=='eccf90da1fbac6bd85c628ffd78df93049e7d267930f9090f857a061a6084540';active=read(previous);assert len(active)==383
active.append({k:y[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}|dict(source_batch='lua-panic-compile-v2-repeat'))
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(instruction_set_sha256=u['instruction_set_sha256'],issues=u['issues'],constructor_ordinal=u['constructor_ordinal'])
entries=collections.Counter();roots=collections.Counter()
for obj in active:
 p=base/obj['source_batch']/obj['folder'];assert sha(p/'function.obj')==obj['object_sha256'];units=read(p/'units.json');assert {u['entry'] for u in units}==set(obj['entries'])
 for u in units:
  key=(obj['module'],u['entry']);assert current[key]['instruction_set_sha256']==u['instruction_set_sha256'];entries[key]+=1
 roots.update(obj['compiled_roots'])
assert len(active)==384 and len(entries)==21176 and set(entries.values())==set(roots.values())=={1}
assert set(entries)=={k for k,v in current.items() if not v['issues']}
constructors=sum(current[k]['constructor_ordinal'] is not None for k in entries);assert constructors==18444
quarantines=[dict(module=k[0],entry=k[1],issues=v['issues']) for k,v in current.items() if v['issues']];assert len(quarantines)==5
summary=read(source/'summary.json');assert summary['counts']['recovery_entry']==21181 and summary['counts']['recovery_instruction']==874279
for k,v in dict(unresolved_indirect_call=9044,unresolved_indirect_jump=430,unresolved_callback_argument=143,unresolved_native_service_control=3,fallthrough_at_fence=5,initial_symbol_dispatch_target_candidate=1,symbol_dispatch_binding_unvalidated=1,stored_lua_panic_target_candidate=2,lua_panic_binding_unvalidated=2).items():assert summary['frontier_counts'][k]==v
runs={}
for suffix in ['lua50-reference-v2-source','lua50-layout-v1','lua-panic-inventory-v1','ghidra-lua-panic-owners-v1','ghidra-lua-panic-targets-v1','ghidra-lua-panic-closure-v1','lua-panic-checked-v1','lua-panic-checks-v2-module','startup-recovery-v28-lua-panic','startup-recovery-v29-lua-panic-repeat','lua-panic-delta-v1','lua-panic-compile-v1','lua-panic-compile-v2-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
checks=(root/'local/runs/20260906-p3-lua-panic-checks-v2-module/stderr.log').read_text(encoding='utf-8');assert 'Ran 76 tests' in checks and checks.rstrip().endswith('OK')
write_json(out/'active-objects.json',active);write_json(out/'quarantined.json',quarantines)
r=dict(status='two independently checked stored Lua panic candidates recovered and compiled; P3 remains open',source=source.relative_to(root).as_posix(),proof=proof,recovery_delta=delta,recovery=summary,active_objects_manifest=(out.relative_to(root)/'active-objects.json').as_posix(),active_objects_sha256=sha(out/'active-objects.json'),previous_active_objects_manifest=previous.relative_to(root).as_posix(),previous_active_objects_sha256=sha(previous),compiled_entries=len(entries),compiled_objects=len(active),compiled_constructors=constructors,remaining_compiler_rejections=0,remaining_quarantines=quarantines,new_compile=y,reproducible_artifacts=repro,runs=runs,
 limitations=['Two constant assignments identify possible mutable global-state panic callbacks at main 0x210ad84. The unknown call and ordinary fallthrough remain; same-object alias and later writes are unvalidated.','Official Lua 5.0.2 LP64 offsets match the observed prefix, but supplied state allocation is 192 bytes versus public 160 and contains an extra allocator at +0xa8. Stock Windows LLP64 places panic at +0x40 rather than supplied +0x50. No unchanged library or host jmp_buf identity is claimed.','All previous entry instruction hashes and root owners remain valid; all 18,444 constructors stay represented once. Five quarantines and every previous unknown-target count remain.','No game-derived object was linked or executed. Native game boot, playable port, P3 closure, P4 startup and new P1 observations remain unestablished.' ],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
r['retained_failures']=['20260906-p3-lua50-reference-v1: rejected two archive convenience symlinks before extraction; v2 records and skips only those exact links','20260906-p3-lua-panic-checks-v1: nonexistent test module name; all 69 loaded tests passed, corrected v2 executes all 76'];write_json(root/'reports/lua-panic-evidence.json',r);compact={k:r[k] for k in ['status','source','compiled_entries','compiled_objects','compiled_constructors','remaining_compiler_rejections','active_objects_manifest','active_objects_sha256']};compact['remaining_quarantines']=len(quarantines);write_json(out/'summary.json',compact);print(json.dumps(compact),flush=True)
