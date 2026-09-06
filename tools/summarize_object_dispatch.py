"""Audit conditional object dispatch candidates, repeated recovery and native objects."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
old=root/'local/cfg/startup-recovery-v15-repeat';left=root/'local/cfg/startup-recovery-v16-dispatch';current=root/'local/cfg/startup-recovery-v17-dispatch-repeat';a=root/'local/compiler-spike/object-dispatch-compile-v1';b=root/'local/compiler-spike/object-dispatch-compile-v2-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
 identities[name]=sha(current/name);assert identities[name]==sha(left/name)
summary=read(current/'summary.json');assert summary['counts']['recovery_entry']==21175 and summary['counts']['recovery_instruction']==874029 and summary['frontier_counts']['unresolved_indirect_call']==9042
proof=read(root/'local/cfg/object-dispatch-checked-v1/checked.json');assert proof['status']=='independent object dispatch candidates passed' and len(proof['proposals'])==3
cohort=read(root/'local/cfg/dispatch-cohort-checked-v1/checked.json');assert cohort['status']=='independent constructor dispatch cohort passed' and cohort['windows']==2165 and cohort['shared_instructions']==25980
windows=read(root/'local/cfg/object-dispatch-closure-checked-v1/checked.json');assert windows['unexplained']==0 and windows['windows']==10 and windows['shared_instructions']==614
old_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(old/'compilation-manifest.jsonl').open(encoding='utf-8'))}
new_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(current/'compilation-manifest.jsonl').open(encoding='utf-8'))};assert all(new_units[k]==v for k,v in old_units.items())
added=set(new_units)-set(old_units);assert len(added)==2
compiled=set();roots={};objects=[]
for directory in [root/'local/compiler-spike/startup-batch-all-v1',root/'local/compiler-spike/startup-fp-recompile-v2-repeat',root/'local/compiler-spike/callback-relocation-compile-v2-repeat',root/'local/compiler-spike/callback-slice-compile-v2-repeat']:
 for r in read(directory/'results.json'):
  if r['status']!='object_built':continue
  compiled.update((r['module'],pc) for pc in r['entries'])
  for pc in r['compiled_roots']:assert pc not in roots;roots[pc]=str(directory/r['folder'])
assert len(compiled)==21163
for x,y in zip(read(a/'results.json'),read(b/'results.json'),strict=True):
 assert x['status']==y['status']=='object_built' and x['input_sha256']==y['input_sha256'] and x['object_sha256']==y['object_sha256']==sha(b/y['folder']/'function.obj')
 folder=b/y['folder'];audit=read(folder/'audit.json');data=read(folder/'input.json');assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions']
 text=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(folder/'function.obj')],text=True);(out/'symbols.txt').write_text(text,encoding='utf-8');actual={int(m[1],16) for m in re.finditer(r'^sub_([0-9a-f]+)\s',text,re.M)};assert actual==set(audit['compiled_roots'])
 for pc in actual:assert pc not in roots;roots[pc]=str(folder)
 for unit in read(folder/'units.json'):assert unit['instruction_set_sha256']==new_units[y['module'],unit['entry']]
 compiled.update((y['module'],pc) for pc in y['entries']);objects.append(dict(folder=y['folder'],object_sha256=y['object_sha256'],object_bytes=y['object_bytes'],entries=y['entries'],roots=sorted(actual),missing_instruction_starts=y['missing_instruction_starts'],external_declarations=y['external_declarations']))
assert added<=compiled and len(compiled)==21165
for directory in [a,b]:
 identity=read(directory/'identity.json');assert identity['source_manifest_sha256']==identities['compilation-manifest.jsonl'] and identity['semantics_sha256']==sha(root/'build/extended-semantics-v9-sqrt/amd64_avx.bc')
runs={}
for suffix in ['object-dispatch-proposals-v1','ghidra-object-dispatch-sources-v1','object-dispatch-source-check-v1','ghidra-object-dispatch-tables-v1','object-dispatch-check-v1','object-dispatch-recovery-checks-v1','startup-recovery-v16-dispatch','startup-recovery-v17-dispatch-repeat','object-dispatch-delta-v1','ghidra-object-dispatch-closure-v1','object-dispatch-closure-check-v1','object-dispatch-compile-v1','object-dispatch-compile-v2-repeat','dispatch-cohort-v1','ghidra-dispatch-cohort-v1','dispatch-cohort-check-v1','dispatch-integrated-checks-v1']:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'Ran 58 tests' in (root/'local/runs/20260906-p3-dispatch-integrated-checks-v1/stderr.log').read_text()
report=dict(status='object dispatch closure evidence pass; P3 remains open',current_directory=current.relative_to(root).as_posix(),summary=summary,reproducibility=identities,prior_instruction_sets_unchanged=21173,new_entries=2,new_instruction_addresses=39,proof=proof,independent_closure=windows,cohort=dict(path='local/cfg/dispatch-cohort-checked-v1/checked.json',sha256=sha(root/'local/cfg/dispatch-cohort-checked-v1/checked.json'),windows=2165,shared_instructions=25980,other_shapes=2630,applied_to_recovery=False),objects=objects,combined_compiled_entries=len(compiled),combined_objects=383,compiled_constructors=18444,remaining_compiler_rejections=2,remaining_quarantined_entries=8,focused_tests=58,runs=runs,gate='P3 remains open: 9,042 indirect-call records, 430 indirect-jump records, eight quarantined boundaries, 143 unknown callback arguments, x87 state counterexamples and native import/callback/exception/control contracts. 21,165 entries compile; no native startup or playable port.',limitations=['Three initial table-slot candidates are applied; each original unknown indirect call is retained.','The independently checked 2,165-constructor cohort is an inventory for the next recovery; only its first representative is currently a table candidate.','Initial object construction, cache identity, table mutation, initialization races/failure and native ABI contracts are unvalidated.','Only specified relocation slots are promoted; adjacent words are not table bounds or code seeds.','Only authored semantic fixtures execute CPU code. These game-derived objects remain unlinked/unexecuted.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/object-dispatch-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],compiled=len(compiled),objects=383,reproducibility=identities,new_object_bytes=sum(r['object_bytes'] for r in objects),unknown_indirect_calls=9042));print(json.dumps(read(out/'summary.json')),flush=True)
