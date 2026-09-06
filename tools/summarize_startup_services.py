"""Audit reproducible service-site closure and add exact new objects to the active census."""
import collections,hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import SPECS,LIBC,MAIN
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
base=root/'local/compiler-spike';cfg=root/'local/cfg'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
first=cfg/'startup-recovery-v23-services';source=cfg/'startup-recovery-v25-services-memory'
repro={}
for name in ['analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json']:
 a=sha(first/name);b=sha(source/name);assert a==b;repro['recovery/'+name]=b
identity=read(source/'identity.json');contracts=read(cfg/'startup-services-checked-v1/contracts.json')
assert identity['service_site_evidence_sha256']==sha(cfg/'startup-services-checked-v1/contracts.json')
assert contracts['status']=='independent Ghidra service-site comparison passed' and len(contracts['contracts'])==3
for p,digest in {**contracts['evidence'],**contracts['references']}.items():assert sha(p)==digest
closure=read(cfg/'ghidra-service-closure-v1/checked.json');assert closure['unexplained']==0 and closure['windows']==11 and closure['shared_instructions']==753
assert sum(len(x['extra']) for x in closure['explained_extra'])==1
delta=read(cfg/'startup-service-delta-v1/delta.json');assert delta['target_db_sha256']==repro['recovery/analysis.sqlite'] and delta['target_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
expected={(s['module'],s['entry']) for s in SPECS}
assert {(r['module'],r['start']) for r in delta['changed']}==expected
old_active=base/'x87-integration-evidence-audit-v2-path/active-objects.json';assert sha(old_active)=='495bb7a294e038b4888afa1955913951c11e89fe245070f1ce1564c606ed4577'
active=read(old_active);assert len(active)==380
prior_keys={(r['module'],e) for r in active for e in r['entries']};assert len(prior_keys)==21170 and not expected&prior_keys
newdir=base/'startup-services-compile-v3-repeat';old=read(base/'startup-services-compile-v2-ready/results.json');new=read(newdir/'results.json');assert len(old)==len(new)==2
newkeys=set();boundaries=[];declarations=set();newbytes=0;newins=0
compile_identity=read(newdir/'identity.json')
assert compile_identity['source_db_sha256']==repro['recovery/analysis.sqlite']
assert compile_identity['source_manifest_sha256']==repro['recovery/compilation-manifest.jsonl']
assert compile_identity['lifter_sha256']==sha(root/'build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe')
assert compile_identity['semantics_sha256']==sha(root/'build/extended-semantics-v31-scale/amd64_avx.bc')
mapping={r['module']:r['logical_base'] for r in compile_identity['module_mapping']}
for x,y in zip(old,new,strict=True):
 assert x['module']==y['module'] and x['entries']==y['entries'] and x['status']==y['status']=='object_built'
 assert y['execution']=='not_executed'
 p=base/'startup-services-compile-v2-ready'/x['folder'];q=newdir/y['folder']
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:
  assert sha(p/name)==sha(q/name);repro[y['folder']+'/'+name]=sha(q/name)
 newkeys.update((y['module'],e) for e in y['entries']);newbytes+=y['object_bytes'];newins+=y['instructions']
 active.append({k:y[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}|dict(source_batch=newdir.name))
 declarations.update(y['external_declarations'])
 for pc in y['missing_instruction_starts']:
  boundaries.append(dict(module=y['module'],rva=pc-mapping[y['module']],object=y['folder']))
assert newkeys==expected
current={};changed_units={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);key=(u['module_sha256'],u['entry']);current[key]=dict(instruction_set_sha256=u['instruction_set_sha256'],issues=u['issues'],constructor_ordinal=u['constructor_ordinal'])
 if key in expected:changed_units[key]=u
entry_owners=collections.defaultdict(list);root_owners=collections.defaultdict(list)
for obj in active:
 p=base/obj['source_batch']/obj['folder'];assert sha(p/'function.obj')==obj['object_sha256']
 units=read(p/'units.json');assert {u['entry'] for u in units}==set(obj['entries'])
 for u in units:
  key=(obj['module'],u['entry']);assert current[key]['instruction_set_sha256']==u['instruction_set_sha256'];entry_owners[key].append(obj['source_batch']+'/'+obj['folder'])
 for pc in obj['compiled_roots']:root_owners[pc].append(obj['source_batch']+'/'+obj['folder'])
assert len(active)==382 and len(entry_owners)==21173 and all(len(x)==1 for x in entry_owners.values()) and all(len(x)==1 for x in root_owners.values())
assert set(entry_owners)=={key for key,value in current.items() if not value['issues']}
constructors=sum(current[key]['constructor_ordinal'] is not None for key in entry_owners);assert constructors==18444
quarantines=[dict(module=k[0],entry=k[1],issues=v['issues']) for k,v in current.items() if v['issues']];assert len(quarantines)==5
for boundary in boundaries:
 h,rva=boundary['module'],boundary['rva'];preceding=[]
 for (module,entry),u in changed_units.items():
  if module!=h:continue
  for ins in u['instructions']:
   if ins['rva']+ins['size']==rva:
    edges=[e for e in u['edges'] if e['source']==ins['rva']]
    preceding.append(dict(entry=entry,instruction=ins,edges=edges))
 assert preceding and any(e['kind']=='unresolved_native_service_control' for r in preceding for e in r['edges'])
 boundary.update(kind='unexpected-return-after-conditional-service-contract',preceding=preceding)
assert len(boundaries)==3
summary=read(source/'summary.json');assert summary['counts']['recovery_instruction']==874265 and summary['counts']['recovery_entry']==21178
for k,v in dict(unresolved_indirect_call=9044,unresolved_indirect_jump=430,unresolved_callback_argument=143,unresolved_native_service_control=3,fallthrough_at_fence=5).items():assert summary['frontier_counts'][k]==v
runs={}
for suffix in ['startup-service-inventory-v1','ghidra-service-boundaries-v1','startup-services-checked-v1','service-site-checks-v1','ghidra-service-closure-v1','startup-recovery-v23-services','startup-recovery-v24-services-repeat','startup-recovery-v25-services-memory','startup-service-delta-v1','startup-services-compile-v1','startup-services-compile-v2-ready','startup-services-compile-v3-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix in ('startup-services-compile-v1','startup-recovery-v24-services-repeat') else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'FileNotFoundError' in (root/'local/runs/20260906-p3-startup-services-compile-v1/stderr.log').read_text()
tests=(root/'local/runs/20260906-p3-service-site-checks-v1/stderr.log').read_text();assert 'Ran 54 tests' in tests and tests.rstrip().endswith('OK')
write_json(out/'active-objects.json',active);write_json(out/'quarantined.json',quarantines);write_json(out/'boundaries.json',boundaries)
report=dict(status='three exact service-call annotations and static object additions pass; P3 remains open',source=str(source.relative_to(root)).replace(chr(92),'/'),recovery=summary,contracts=contracts,independent_window_closure=closure,recovery_delta=delta,active_objects_manifest=(out.relative_to(root)/'active-objects.json').as_posix(),active_objects_sha256=sha(out/'active-objects.json'),previous_active_objects_manifest=old_active.relative_to(root).as_posix(),previous_active_objects_sha256=sha(old_active),compiled_entries=len(entry_owners),compiled_objects=len(active),compiled_constructors=constructors,remaining_compiler_rejections=0,remaining_quarantines=quarantines,new_object_bytes=newbytes,new_instruction_count=newins,new_boundaries=boundaries,new_external_declarations=sorted(declarations),reproducible_artifacts=repro,runs=runs,
 signal_import=dict(module=LIBC,entry=0x12f00,site=0x13027,plt=0x300,nid='VADc3MNQ3cM',name='signal',arguments={'edi':9,'rsi':0},classification='Tail service call setting the signal disposition, not raising a signal or registering a non-null handler. Exact console result/errno, signal-number mapping and native binding remain unvalidated; original recovery record remains unchanged.'),
 retained_memory_repeat='Recovery v24 completed decoding/manifests but was stopped during integrity_check under severe host memory pressure: 959652 KiB free of 33335168 KiB, 545586 process read operations / 3345372046 bytes after about fourteen minutes. A 1206054912-byte read-only cache warmup took 45.43 seconds without prompt completion. Only the verified experiment child was stopped; no unrelated process was closed. V25 releases recovery maps and gives SQLite a 64 MiB connection-local cache before the same mandatory integrity check. The stopped database/manifests/source snapshot/logs remain preserved.',
 retained_failure='Compile v1 was dispatched before the delta selection file existed. It failed with FileNotFoundError before lifting/compiling; source snapshot and logs are preserved. V2 starts after delta completion and V3 repeats its artifacts.',
 limitations=['All no-ordinary-return annotations are conditional API/control contracts, not native service implementations. The debug-service contract applies only to the exact supplied abort-wrapper site and constants.','The two new objects are static compilation evidence only; three unexpected-return paths and all service/callback/exception/indirect declarations remain explicit. No game-derived object was linked or executed.','The five throw/rethrow and main nonlocal-transfer quarantines remain. Generic unresolved virtual calls were not assumed to return or terminate.','No unknown callback or indirect target was removed. Constructor tables and callback state remain mutable; unwind fences are not proven function boundaries.','P1 baseline observations, Intel-only authored semantic checks and native game execution remain separate. No native game boot, playable port or P3/P4 pass is claimed.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/startup-services-evidence.json',report)
compact={k:report[k] for k in ['status','source','compiled_entries','compiled_objects','compiled_constructors','remaining_compiler_rejections','active_objects_manifest','active_objects_sha256','new_object_bytes','new_instruction_count']};compact['remaining_quarantines']=len(quarantines);write_json(out/'summary.json',compact);print(json.dumps(compact),flush=True)
