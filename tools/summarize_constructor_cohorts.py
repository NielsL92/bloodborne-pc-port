"""Audit checked constructor cohorts, subobject closure and preserved unknown calls."""
import hashlib,json,re,sqlite3,subprocess,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
old=root/'local/cfg/startup-recovery-v17-dispatch-repeat';left=root/'local/cfg/startup-recovery-v19-subobject';current=root/'local/cfg/startup-recovery-v20-subobject-repeat';a=root/'local/compiler-spike/subobject-compile-v1';b=root/'local/compiler-spike/subobject-compile-v2-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
 identities[name]=sha(current/name);assert identities[name]==sha(left/name)
summary=read(current/'summary.json');assert summary['counts']['recovery_entry']==21178 and summary['counts']['recovery_instruction']==874266 and summary['frontier_counts']['unresolved_indirect_call']==9044
proof_path=root/'local/cfg/object-dispatch-expanded-v3-subobject/checked.json';proof=read(proof_path);assert proof['status']=='independent object dispatch candidates passed' and len(proof['proposals'])==4767
cohorts=[read(root/f'local/cfg/{name}/checked.json') for name in ['dispatch-cohort-checked-v1','subobject-cohort-checked-v1']]
assert [r['windows'] for r in cohorts]==[2165,2596] and [r['shared_instructions'] for r in cohorts]==[25980,33917]
sets=[{(r['module'],r['entry'],r['site']) for r in cohort['records']} for cohort in cohorts];assert not sets[0]&sets[1]
constructor_sites=sets[0]|sets[1];assert len(constructor_sites)==4761
windows=read(root/'local/cfg/subobject-closure-checked-v1/checked.json');assert windows['unexplained']==0 and windows['windows']==11
old_db=sqlite3.connect((old/'analysis.sqlite').as_uri()+'?mode=ro',uri=True);db=sqlite3.connect((current/'analysis.sqlite').as_uri()+'?mode=ro',uri=True)
unknown_query="select module,entry,source,kind,detail from recovery_edge where kind like 'unresolved_%'"
assert set(old_db.execute(unknown_query))<=set(db.execute(unknown_query))
proof_digest=sha(proof_path)
actual={(h,e,site,target) for h,e,site,target,detail in db.execute("select module,entry,source,target,detail from recovery_edge where kind='initial_object_dispatch_target_candidate'") if json.loads(detail)['evidence_sha256']==proof_digest}
expected={(r['module'],r['call_entry'],r['call'],r['target']) for r in proof['proposals']};assert actual==expected and len(actual)==4767
assert constructor_sites<={(h,e,site) for h,e,site,target in actual}
old_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(old/'compilation-manifest.jsonl').open(encoding='utf-8'))}
new_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(current/'compilation-manifest.jsonl').open(encoding='utf-8'))};assert all(new_units[k]==v for k,v in old_units.items())
added=set(new_units)-set(old_units);assert len(added)==3
compiled=set();roots={};objects=[]
for directory in [root/'local/compiler-spike/startup-batch-all-v1',root/'local/compiler-spike/startup-fp-recompile-v2-repeat',root/'local/compiler-spike/callback-relocation-compile-v2-repeat',root/'local/compiler-spike/callback-slice-compile-v2-repeat',root/'local/compiler-spike/object-dispatch-compile-v2-repeat']:
 for r in read(directory/'results.json'):
  if r['status']!='object_built':continue
  compiled.update((r['module'],pc) for pc in r['entries'])
  for pc in r['compiled_roots']:assert pc not in roots;roots[pc]=str(directory/r['folder'])
assert len(compiled)==21165
for x,y in zip(read(a/'results.json'),read(b/'results.json'),strict=True):
 assert x['status']==y['status']=='object_built' and x['input_sha256']==y['input_sha256'] and x['object_sha256']==y['object_sha256']==sha(b/y['folder']/'function.obj')
 folder=b/y['folder'];audit=read(folder/'audit.json');data=read(folder/'input.json');assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions']
 text=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(folder/'function.obj')],text=True);(out/'symbols.txt').write_text(text,encoding='utf-8');actual={int(m[1],16) for m in re.finditer(r'^sub_([0-9a-f]+)\s',text,re.M)};assert actual==set(audit['compiled_roots'])
 for pc in actual:assert pc not in roots;roots[pc]=str(folder)
 for unit in read(folder/'units.json'):assert unit['instruction_set_sha256']==new_units[y['module'],unit['entry']]
 compiled.update((y['module'],pc) for pc in y['entries']);objects.append(dict(folder=y['folder'],object_sha256=y['object_sha256'],object_bytes=y['object_bytes'],entries=y['entries'],roots=sorted(actual),missing_instruction_starts=y['missing_instruction_starts'],external_declarations=y['external_declarations']))
assert added<=compiled and len(compiled)==21168
for directory in [a,b]:
 identity=read(directory/'identity.json');assert identity['source_manifest_sha256']==identities['compilation-manifest.jsonl'] and identity['semantics_sha256']==sha(root/'build/extended-semantics-v9-sqrt/amd64_avx.bc')
runs={}
for suffix in ['object-dispatch-proposals-v2-nested','ghidra-object-dispatch-sources-v2-nested','object-dispatch-source-check-v2-nested','ghidra-object-dispatch-tables-v2-nested','object-dispatch-check-v2-nested','dispatch-cohort-expand-v1','startup-recovery-v18-cohort','subobject-cohort-v1','object-dispatch-proposals-v3-subobject','ghidra-subobject-cohort-v1','ghidra-object-dispatch-sources-v3-subobject','subobject-cohort-check-v1','object-dispatch-source-check-v3-subobject','ghidra-object-dispatch-tables-v3-subobject','object-dispatch-check-v3-subobject','dispatch-cohort-expand-v2','dispatch-cohort-expand-v3-subobject','startup-recovery-v19-subobject','startup-recovery-v20-subobject-repeat','subobject-integrated-checks-v1','subobject-delta-v1','ghidra-subobject-closure-v1','subobject-closure-check-v1','subobject-compile-v1','subobject-compile-v2-repeat']:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'Ran 64 tests' in (root/'local/runs/20260906-p3-subobject-integrated-checks-v1/stderr.log').read_text()
report=dict(status='constructor cohort closure evidence pass; P3 remains open',current_directory=current.relative_to(root).as_posix(),summary=summary,reproducibility=identities,prior_instruction_sets_unchanged=21175,new_entries=3,new_instruction_addresses=237,proof=dict(path=proof_path.relative_to(root).as_posix(),sha256=sha(proof_path),proposals=4767,independent_checks=proof['independent_checks'],source_check=proof['source_check'],cohort_expansions=proof['cohort_expansions']),independent_closure=windows,cohorts=[dict(windows=r['windows'],shared_instructions=r['shared_instructions'],source_db_sha256=r['source_db_sha256'],matches_sha256=r['matches_sha256']) for r in cohorts],constructor_call_sites_with_checked_candidate=4761,constructor_same_operand_sites_remaining=34,all_prior_unknown_records_retained=True,objects=objects,combined_compiled_entries=len(compiled),combined_objects=384,compiled_constructors=18444,remaining_compiler_rejections=2,remaining_quarantined_entries=8,focused_tests=64,runs=runs,gate='P3 remains open: 9,044 indirect-call records, 430 indirect-jump records, eight quarantined boundaries, 143 unknown callback arguments, x87 state counterexamples and native import/callback/exception/control contracts. 21,168 entries compile; no native startup or playable port.',limitations=['4,767 initial candidate records retain all unknown runtime calls; this is not executed or immutable dispatch coverage.','Two exact constructor sequences cover 4,761 of 4,795 [RAX+0x20] constructor call records; 34 use noncontiguous cache-register provenance and remain separate.','The second factory returns a base object whose +0x458 subobject receives initial table 0x53b2e70. Its observed +0x58 method reaches additional allocator and lock dependencies.','No declaration of table extent, successful native initialization, static uniqueness or game boot is made.','Retained v18 is an intermediate cohort expansion; v19/v20 are the repeated combined current manifests.','Only authored semantic fixtures execute CPU code. Game-derived objects remain unlinked/unexecuted.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/constructor-cohort-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],compiled=len(compiled),objects=384,reproducibility=identities,new_object_bytes=sum(r['object_bytes'] for r in objects),unknown_indirect_calls=9044,checked_initial_site_candidates=4767));print(json.dumps(read(out/'summary.json')),flush=True)
