"""Verify repeated complete source-exit compilation and publish a replacement manifest."""
import argparse,collections,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike');plan=base/'source-exit-plan-v1';first=base/'source-exit-compile-v2-all';repeat=base/'source-exit-compile-v3-repeat';source=Path('local/cfg/startup-recovery-v31-conditional-repeat')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
identity=read(repeat/'identity.json');assert identity==read(first/'identity.json');assert sha(source/'analysis.sqlite')==identity['source_db_sha256'];assert sha(source/'compilation-manifest.jsonl')==identity['source_manifest_sha256']
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 row=json.loads(line);current[row['module_sha256'],row['entry']]=dict(hash=row['instruction_set_sha256'],ctor=row['constructor_ordinal'],issues=row['issues'])
rows=read(plan/'objects.json');before=read(first/'results.json');after=read(repeat/'results.json');assert len(rows)==len(before)==len(after)==386
active=[];entries=collections.Counter();roots=collections.Counter();guarded=set();instruction_count=0
for row,one,two in zip(rows,before,after,strict=True):
 assert one==two and two['status']=='object_built' and two['index']==row['index'];folder=repeat/two['folder']
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:assert sha(first/two['folder']/name)==sha(folder/name)
 assert sha(folder/'function.obj')==two['object_sha256'];audit=read(folder/'audit.json');data=read(folder/'input.json');assert audit['compiled_roots']==row['compiled_roots']==data['roots'];assert set(audit['decoded_addresses'])=={i['address'] for i in data['instructions']} and not audit['unvisited_manifest_instructions'];assert two['missing_instruction_starts']==row['original_missing_instruction_starts'];instruction_count+=len(data['instructions'])
 for u in read(folder/'units.json'):
  key=two['module'],u['entry'];assert u['instruction_set_sha256']==current[key]['hash'] and not current[key]['issues'];entries[key]+=1
 roots.update(two['compiled_roots']);guarded.update(r['source'] for r in audit['call_return_checks'] if r['no_normal_return'])
 active.append(dict(source_batch=repeat.name,**{key:two[key] for key in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']}))
assert len(entries)==21181 and len(roots)==21282 and set(entries)==set(current) and set(entries.values())=={1} and set(roots.values())=={1};assert sum(current[k]['ctor'] is not None for k in entries)==18444;assert instruction_count==874279 and len(guarded)==4305
checks=read(base/'source-exit-checks-v3-repeat/summary.json');assert checks['result']['cases']==28672 and checks['result']['hypercall_faults']==2048
for name in checks['artifact_sha256']:assert sha(base/'source-exit-checks-v2-flags'/name)==sha(base/'source-exit-checks-v3-repeat'/name)==checks['artifact_sha256'][name]
call=read(base/'call-return-checks-v5-source-exits/summary.json');assert call['result']['cases']==14336 and call['result']['native_faults']==8192
# Extra provenance stores change pre-O2 IR; the ordinary-call regression retains identical native object and outcome.
for name in ['function.obj','execute.stdout']:assert sha(base/'call-return-checks-v5-source-exits'/name)==sha(base/'call-return-checks-v4-repeat'/name)
assert read(base/'call-return-inputs-v3-source-exits/summary.json')['rejected']==12;assert read(base/'sparse-checks-v5-source-exits/summary.json')['native']['aot_cases']==8192
compiler=Path('build/sparse-lift-v11-source-exits');assert identity['lifter_sha256']==sha(compiler/'bb-sparse-lift.exe')==checks['lifter_sha256'];assert sha('native/sparse_lift/main.cpp')==read(compiler/'identity.json')['driver_source_sha256']
runs={}
for suffix in ['source-exit-checks-v2-flags','source-exit-checks-v3-repeat','source-exit-plan-v1','source-exit-compile-v1-preflight','source-exit-compile-v2-all','source-exit-compile-v3-repeat','call-return-checks-v5-source-exits','call-return-inputs-v3-source-exits','sparse-checks-v5-source-exits','control-origin-checks-v1']:
 path=Path('local/runs')/('20260906-p3-'+suffix);manifest=read(path/'manifest.json');assert manifest['status']=='pass'
 with zipfile.ZipFile(path/'sources.zip') as archive:
  for file,digest in manifest['source_sha256'].items():assert hashlib.sha256(archive.read(file.replace(chr(92),'/'))).hexdigest()==digest
 runs[path.name]=dict(source_commit=manifest['project_commit'],sources_sha256=sha(path/'sources.zip'),elapsed_seconds=manifest['elapsed_seconds'])
write_json(a.out/'active-objects.json',active);summary=dict(status='complete source-aware object set repeats and matches all current recovered entries',active_manifest=str(a.out/'active-objects.json'),active_manifest_sha256=sha(a.out/'active-objects.json'),compiled_objects=len(active),compiled_entries=len(entries),compiled_roots=len(roots),compiled_constructors=18444,instructions=instruction_count,unique_guarded_nonreturn_sites=len(guarded),compile=read(repeat/'summary.json'),transfer_checks=checks,call_return_checks=call,identity=identity,runs=runs,limitations=['All previous objects and runs remain preserved; this manifest replaces the entire prior set.','Compiler audit counts include structurally unreachable continuation blocks. Saved bitcode is semantic-inlined before clang O2, not a final machine-code exit count.','Source/expected/actual interfaces do not establish production native handlers, source-edge dispatch authorization, import service support or compatible guest unwind.','No game-derived object linked or executed.'],p3_gate_passed=False,native_game_boot=False);write_json(a.out/'evidence.json',summary);print(json.dumps({k:summary[k] for k in ['status','active_manifest','active_manifest_sha256','compiled_objects','compiled_entries','compiled_roots','compiled_constructors','unique_guarded_nonreturn_sites']}),flush=True)
