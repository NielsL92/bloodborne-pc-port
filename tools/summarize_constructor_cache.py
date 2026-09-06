"""Audit bounded cache slices, preserved compilation ownership and candidate records."""
import hashlib,json,sqlite3,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
old=root/'local/cfg/startup-recovery-v20-subobject-repeat';left=root/'local/cfg/startup-recovery-v21-cache';current=root/'local/cfg/startup-recovery-v22-cache-repeat';identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
 identities[name]=sha(current/name);assert identities[name]==sha(left/name)
summary=read(current/'summary.json');assert summary['counts']['recovery_entry']==21178 and summary['counts']['recovery_instruction']==874266 and summary['frontier_counts']['initial_object_dispatch_target_candidate']==4801
old_units={(r['module_sha256'],r['entry']):r['instruction_set_sha256'] for r in map(json.loads,(old/'compilation-manifest.jsonl').open(encoding='utf-8'))};new_units={(r['module_sha256'],r['entry']):r['instruction_set_sha256'] for r in map(json.loads,(current/'compilation-manifest.jsonl').open(encoding='utf-8'))};assert old_units==new_units
old_db=sqlite3.connect((old/'analysis.sqlite').as_uri()+'?mode=ro',uri=True);db=sqlite3.connect((current/'analysis.sqlite').as_uri()+'?mode=ro',uri=True)
unknown="select module,entry,source,kind,detail from recovery_edge where kind like 'unresolved_%'";assert set(old_db.execute(unknown))==set(db.execute(unknown))
proof_path=root/'local/cfg/object-dispatch-expanded-v4-cache/checked.json';proof=read(proof_path);digest=sha(proof_path)
actual={(h,e,s,t) for h,e,s,t,detail in db.execute("select module,entry,source,target,detail from recovery_edge where kind='initial_object_dispatch_target_candidate'") if json.loads(detail)['evidence_sha256']==digest};expected={(r['module'],r['call_entry'],r['call'],r['target']) for r in proof['proposals']};assert actual==expected and len(actual)==4801
constructors=set(db.execute('select module,target from initializer_slot'));calls={(h,e,s) for h,e,s in db.execute("select module,entry,source from recovery_edge where kind='unresolved_indirect_call' and detail='qword ptr [rax + 0x20]'") if (h,e) in constructors};assert len(calls)==4795 and calls<={(h,e,s) for h,e,s,t in actual}
slices_path=root/'local/cfg/dispatch-cache-slices-checked-v1/checked.json';slices=read(slices_path);assert slices['status']=='independent dispatch cache slices passed' and len(slices['records'])==34 and all(r['complete'] and r['independent']['complete'] for r in slices['records'])
windows=read(root/'local/cfg/dispatch-cache-window-checked-v1/checked.json');assert windows['unexplained']==0 and windows['windows']==3 and windows['shared_instructions']==1608
regression=sha(root/'local/cfg/callback-slices-v1/slices.json')
for name in ['callback-slices-memo-regression-v1','callback-slices-worklist-regression-v1']:assert sha(root/'local/cfg'/name/'slices.json')==regression
compiled=set();object_count=0;object_inputs=[]
for name in ['startup-batch-all-v1','startup-fp-recompile-v2-repeat','callback-relocation-compile-v2-repeat','callback-slice-compile-v2-repeat','object-dispatch-compile-v2-repeat','subobject-compile-v2-repeat']:
 directory=root/'local/compiler-spike'/name
 for r in read(directory/'results.json'):
  if r['status']!='object_built':continue
  folder=directory/r['folder'];assert sha(folder/'function.obj')==r['object_sha256'];object_count+=1
  for unit in read(folder/'units.json'):assert new_units[r['module'],unit['entry']]==unit['instruction_set_sha256']
  for pc in r['entries']:assert (r['module'],pc) not in compiled;compiled.add((r['module'],pc))
 object_inputs.append(dict(directory=directory.relative_to(root).as_posix(),results_sha256=sha(directory/'results.json')))
assert len(compiled)==21168 and object_count==384 and constructors<=compiled
runs={};failures={'dispatch-cache-slices-v1':'Stopped the verified slice child after 164 seconds of repeated branch-join enumeration; original run, source and empty logs retained.','dispatch-cache-slices-v2-memo':'Memoized traversal hit Python recursion depth on the long 0x20b8c80 slice; partial stdout and traceback retained. The bounded worklist replaces recursion.'}
for suffix in ['dispatch-cache-slices-v1','cache-slice-memo-checks-v1','dispatch-cache-slices-v2-memo','callback-slices-memo-regression-v1','cache-slice-worklist-checks-v1','dispatch-cache-slices-v3-worklist','ghidra-dispatch-cache-slices-v1','callback-slices-worklist-regression-v1','dispatch-cache-slices-check-v1','dispatch-cache-expansion-v1','startup-recovery-v21-cache','startup-recovery-v22-cache-repeat','dispatch-cache-window-check-v1']:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']==('failed' if suffix in failures else 'pass')
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'],retained_failure=failures.get(suffix))
assert 'Ran 69 tests' in (root/'local/runs/20260906-p3-cache-slice-worklist-checks-v1/stderr.log').read_text()
report=dict(status='constructor cache slice evidence pass; P3 remains open',current_directory=current.relative_to(root).as_posix(),summary=summary,reproducibility=identities,all_instruction_sets_unchanged=21178,all_prior_unknown_records_unchanged=True,proof=dict(path=proof_path.relative_to(root).as_posix(),sha256=sha(proof_path),proposals=4801,cache_slice_expansion=proof['cache_slice_expansion']),slices=dict(path=slices_path.relative_to(root).as_posix(),sha256=sha(slices_path),complete=34,conditional_sysv_call_counts=[dict(entry=r['entry'],site=r['tail']['dispatch_site'],calls=len(r['conditional_normal_sysv_returns'])) for r in slices['records']]),independent_windows=windows,callback_regression_sha256=regression,constructor_same_operand_sites_with_initial_candidate=4795,combined_compiled_entries=21168,combined_objects=384,compiled_constructors=18444,retained_object_inputs=object_inputs,remaining_compiler_rejections=2,remaining_quarantined_entries=8,focused_tests=69,runs=runs,gate='P3 remains open: 9,044 indirect-call records, 430 indirect-jump records, eight quarantined boundaries, 143 unknown callback arguments, x87 state counterexamples and native import/callback/exception/control contracts. 21,168 entries compile; no native startup or playable port.',limitations=['All 4,795 constructor [RAX+0x20] records have checked conditional initial candidates; every runtime unknown call remains. This is not complete indirect or execution coverage.','The worklist unions constants over recovered predecessors, reports cycles/metadata roots/unsupported writes, and visits each state once within the explicit budget.','Previous objects are reused only after exact per-entry instruction and object-byte identity checks; no new body or object is claimed.','No game-derived CPU code was linked or executed.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/constructor-cache-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],compiled=21168,objects=384,proposals=4801,constructor_sites=4795,reproducibility=identities));print(json.dumps(read(out/'summary.json')),flush=True)
