"""Audit the P3 startup checkpoint and preserve unresolved evidence, including failed runs."""
import collections,hashlib,json,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();a=root/'local/cfg/startup-recovery-v4';b=root/'local/cfg/startup-recovery-v5-repeat'
assert sha(a/'analysis.sqlite')==sha(b/'analysis.sqlite')
assert sha(a/'compilation-manifest.jsonl')==sha(b/'compilation-manifest.jsonl')
assert sha(a/'frontier.jsonl')==sha(b/'frontier.jsonl')
assert json.loads((a/'constructor-order.json').read_text())==json.loads((root/'local/cfg/startup-v1/roots.json').read_text())
summary=json.loads((a/'summary.json').read_text());assert summary['constructors']=={'decoded_with_explicit_boundaries':18444}
assert summary['decode_issue_kinds']=={'fallthrough_at_fence':146}
db=sqlite3.connect(f'{(a/"analysis.sqlite").as_uri()}?mode=ro',uri=True)
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
# Every explicit direct dependency request was visited. This excludes unresolved/candidate addresses.
missing=db.execute('SELECT DISTINCT q.module,q.target FROM recovery_request q LEFT JOIN recovery_entry e ON e.module=q.module AND e.start=q.target WHERE e.start IS NULL').fetchall();assert not missing
artifacts={}
for name,path in {
 'recovery_v2':'local/cfg/startup-recovery-v2/summary.json','recovery_v3':'local/cfg/startup-recovery-v3/summary.json',
 'recovery':'local/cfg/startup-recovery-v4/summary.json','repeat':'local/cfg/startup-recovery-v5-repeat/summary.json',
 'ghidra_boundaries':'local/cfg/ghidra-recovery-v1/summary.json','ghidra_tables':'local/cfg/ghidra-startup-tables-v1/summary.json',
 'table_bytes':'local/cfg/startup-table-bytes-v1/tables.json','compilation':'local/compiler-spike/startup-manifest-v1/summary.json'}.items():
 artifacts[name]=dict(path=path,sha256=sha(root/path),result=json.loads((root/path).read_text()))
# Explain decoder differences from shared no-return contracts; retain all other disagreements.
comparisons=json.loads((root/'local/cfg/ghidra-recovery-v1/comparison.json').read_text());explained=[];unresolved=[]
for c in comparisons:
 assert not c['boundary_disagreements']
 if c['equal']:continue
 h,start=c['module'],c['start'];extras=c['only_ghidra']
 contracts=[]
 for source,detail in db.execute("SELECT source,detail FROM recovery_edge WHERE module=? AND entry=? AND kind='annotated_control_contract_requires_runtime'",(h,start)):
  row=db.execute('SELECT size FROM recovery_instruction WHERE module=? AND rva=?',(h,source)).fetchone()
  if row and extras and source+row[0]==min(extras):contracts.append(dict(source=source,contract=detail))
  raw_path=root/'local/cfg/ghidra-recovery-v1'/db.execute('SELECT name FROM module WHERE hash=?',(h,)).fetchone()[0]/'ghidra.json'
 raw_fn=next(fn for fn in json.loads(raw_path.read_text()) if fn['start']==start)
 raw_ins={r['rva']:r for r in raw_fn['instructions']}
 suffix_queue=collections.deque([min(extras)] if contracts and extras else []);suffix_seen=set()
 while suffix_queue:
  at=suffix_queue.popleft()
  if at in suffix_seen or at not in raw_ins:continue
  suffix_seen.add(at);ins=raw_ins[at];flow=ins['flow'];after=at+ins['length']
  if 'JUMP' in flow:suffix_queue.extend(ins['targets'])
  if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and not ins['text'].startswith(('RET','UD2','HLT')):suffix_queue.append(after)
 if not c['only_recovery'] and contracts and set(extras)<=suffix_seen:
  explained.append(dict(module=h,entry=start,extra_addresses=extras,contracts=contracts,classification='Ghidra follows ordinary fallthrough after an independently documented nonreturn call; no instruction-byte disagreement'))
 else:unresolved.append(c)
write_json(root/'reports/ghidra-startup-disputes.json',dict(explained=explained,unresolved=unresolved))
# Exact instruction identities from the independently recovered library switches.
table_checks=[]
for fn in json.loads((root/'local/cfg/ghidra-startup-tables-v1/ghidra.json').read_text()):
 h=artifacts['ghidra_tables']['result']['module_sha256'];entry=fn['entry']
 ours={rva:(size,raw) for rva,size,raw in db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=?',(h,entry))}
 theirs={r['rva']:(r['length'],r['bytes']) for r in fn['instructions']}
 common=set(ours)&set(theirs);assert all(ours[rva]==theirs[rva] for rva in common)
 table_checks.append(dict(entry=entry,shared_instructions=len(common),only_recovery=sorted(set(ours)-set(theirs)),only_ghidra=sorted(set(theirs)-set(ours))))
# Object construction has an identity link back to the current unchanged constructor instructions.
compiler=root/'local/compiler-spike/startup-manifest-v1'
compiled=json.loads((compiler/'results.json').read_text());assert len(compiled)==128 and all(r['status']=='object_built' for r in compiled)
for r in compiled:
 folder=compiler/f"{r['entry']:x}";unit=json.loads((folder/'manifest.json').read_text())
 assert sha(folder/'function.obj')==r['object_sha256']
 rows=db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(unit['module_sha256'],unit['entry'])).fetchall()
 assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()==unit['instruction_set_sha256']
# Summarize remaining range-boundary causes without assuming a final call is nonreturning.
endings=collections.Counter();examples=[]
for h,entry,rva,kind,detail in db.execute('SELECT * FROM recovery_issue ORDER BY module,entry,rva'):
 target=db.execute("SELECT target,kind,detail FROM recovery_edge WHERE module=? AND entry=? AND source=? AND kind NOT IN ('fallthrough','callback_argument_candidate') ORDER BY kind",(h,entry,rva)).fetchall()
 endings[detail]+=1
 if len(examples)<20:examples.append(dict(module=h,entry=entry,rva=rva,kind=kind,instruction=detail,edges=target))
run_names=['startup-inspection-v1','recovery-reader-checks-v1','recovery-reader-checks-v2','recovery-reader-checks-v3','recovery-reader-checks-v4',
 'startup-recovery-v1','startup-recovery-v2','startup-recovery-v3','startup-recovery-v4','startup-recovery-v5-repeat',
 'startup-recovery-audit-v1','startup-recovery-audit-v2','ghidra-recovery-v1','startup-contract-identities-v1','startup-manifest-compile-v1','ghidra-startup-tables-v1','startup-table-bytes-v1']
runs={}
for suffix in run_names:
 name='20260905-p3-'+suffix;manifest=json.loads((root/'local/runs'/name/'manifest.json').read_text())
 assert manifest['status']!='running'
 runs[name]=dict(status=manifest['status'],exit_code=manifest.get('exit_code'),source_commit=manifest['project_commit'],elapsed_seconds=manifest['elapsed_seconds'],source_archive_sha256=sha(root/'local/runs'/name/'sources.zip'))
assert all(r['status']=='pass' for name,r in runs.items() if name not in ('20260905-p3-recovery-reader-checks-v1','20260905-p3-startup-recovery-v1'))
report=dict(status='startup recovery evidence consistency pass; P3 gate open',artifacts=artifacts,runs=runs,
 reproducibility=dict(database_sha256=sha(a/'analysis.sqlite'),manifest_sha256=sha(a/'compilation-manifest.jsonl'),frontier_sha256=sha(a/'frontier.jsonl'),ordered_roots_equal=True,explicit_requested_entries_missing=missing),
 ghidra_disputes=dict(details_path='reports/ghidra-startup-disputes.json',details_sha256=sha(root/'reports/ghidra-startup-disputes.json'),explained_nonreturn_fallthrough=len(explained),remaining_reachability_disagreements=unresolved,table_instruction_comparisons=table_checks),
 remaining_boundary_endings=dict(endings),remaining_boundary_examples=examples,
 retained_failures=[dict(run='20260905-p3-recovery-reader-checks-v1',reason='Overlap was correctly detected as overlapping bytes; assertion incorrectly required overlapping target. Assertion fixed, negative fixture preserved.'),
 dict(run='20260905-p3-startup-recovery-v1',reason='Overexpanded pointer arguments into executable-mapped strings/data. Recovery evidence retained. Obsolete slow export stopped after v2/v3 succeeded; its child exit was recorded as failure. Fresh exporter uses indexed ownership-first queries.')],
 gate='P3 not passed: all 18444 initial constructor entries decoded, but 8980 indirect call records, 421 indirect jump records, 146 fallthrough-boundary findings, mutable/callback targets, and native import/control/exception contracts remain unresolved. 128 objects are compilation evidence only.',
 baseline_execution='No new P1 captures; existing clinic movement/save/quit/reload remains separately instrumented shadPS4 evidence.',native_game_boot=False,native_port_playable=False)
continuation=root/'reports/startup-closure-evidence.json'
if continuation.exists():
 latest=json.loads(continuation.read_text())
 assert latest['status']=='startup closure continuation evidence consistency pass; P3 gate open'
 report['historical_v4_gate']=report['gate'];report['gate']=latest['gate']
 report['current_directory']=latest['current_directory']
 report['continuation']=dict(path=str(continuation.relative_to(root)),sha256=sha(continuation),result=latest)
sparse=root/'reports/sparse-compiler-evidence.json'
if sparse.exists():
 latest=json.loads(sparse.read_text())
 assert latest['status']=='sparse compiler evidence consistency pass; P3 gate open'
 report['sparse_compiler']=dict(path=str(sparse.relative_to(root)),sha256=sha(sparse),result=latest)
 report['gate']=latest['gate']
latest_path=root/'reports/startup-v9-evidence.json'
if latest_path.exists():
 latest=json.loads(latest_path.read_text())
 assert latest['status']=='startup v9 evidence consistency pass; P3 gate open'
 report['current_directory']=latest['current_directory'];report['gate']=latest['gate']
 report['startup_v9']=dict(path=str(latest_path.relative_to(root)),sha256=sha(latest_path),result=latest)
 batch=root/'reports/startup-batch-evidence.json'
 if batch.exists():report['startup_batch']=dict(path=str(batch.relative_to(root)),sha256=sha(batch),result=json.loads(batch.read_text()))
bmi=root/'reports/bmi-trap-evidence.json'
if bmi.exists():report['bmi_trap']=dict(path=str(bmi.relative_to(root)),sha256=sha(bmi),result=json.loads(bmi.read_text()))
vector=root/'reports/vector-semantics-evidence.json'
if vector.exists():report['vector_semantics']=dict(path=str(vector.relative_to(root)),sha256=sha(vector),result=json.loads(vector.read_text()))
write_json(root/'reports/startup-recovery-evidence.json',report)
print(json.dumps(dict(status=report['status'],reproducibility=report['reproducibility'],ghidra_explained=len(explained),ghidra_unresolved=len(unresolved),table_checks=table_checks,boundary_endings=dict(endings))),flush=True)
