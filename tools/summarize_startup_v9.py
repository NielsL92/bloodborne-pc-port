"""Audit the allocation-error and nullable-callback recovery continuation."""
import collections,hashlib,json,sqlite3,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();before=root/'local/cfg/startup-recovery-v7-repeat';a=root/'local/cfg/startup-recovery-v8';b=root/'local/cfg/startup-recovery-v9-repeat'
repeat={name:sha(b/name) for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json')}
assert all(sha(a/name)==digest for name,digest in repeat.items())
assert all(sha(root/'local/cfg/startup-recovery-v10-zero-guard'/name)==digest for name,digest in repeat.items())
assert sha(before/'constructor-order.json')==repeat['constructor-order.json']
summary=json.loads((b/'summary.json').read_text());assert summary['counts']['recovery_entry']==21160 and summary['counts']['recovery_instruction']==873581 and summary['counts']['recovery_issue']==8
assert summary['frontier_counts']['unresolved_callback_argument']==155 and summary['frontier_counts']['callback_contract_null_argument']==15
changes=json.loads((root/'local/cfg/callback-zero-delta-v1/changes.json').read_text());assert len(changes['resolved_nullable_arguments'])==15 and len(changes['removed_issues'])==1 and len(changes['changed_instruction_sets'])==1
old=json.loads((root/'local/cfg/derived-control-checked-v1/contracts.json').read_text());new=json.loads((root/'local/cfg/bad-alloc-control-checked-v1/contracts.json').read_text())
assert len(new['contracts'])==29 and new['status']=='independent Ghidra control comparison passed'
lookup={r['id']:r for r in new['contracts']};assert all(lookup[r['id']]==r for r in old['contracts'])
added=[r for r in new['contracts'] if r['id'] not in {x['id'] for x in old['contracts']}];assert len(added)==1 and added[0]['rva']==0x5ebd0 and len(added[0]['instructions'])==11
assert json.loads((root/'local/cfg/ghidra-bad-alloc-v1/summary.json').read_text())['equal']==29
folder=root/'local/cfg/ghidra-callback-zero-v1';ghidra=json.loads((folder/'summary.json').read_text());assert ghidra['entries']==10 and ghidra['boundary_disagreements']==0
compare=json.loads((folder/'comparison.json').read_text());assert all(not c['only_recovery'] for c in compare)
db=sqlite3.connect(f'{(b/"analysis.sqlite").as_uri()}?mode=ro',uri=True);names=dict(db.execute('SELECT hash,name FROM module'));raw={};disputes=[]
for c in compare:
 h,entry=c['module'],c['start']
 if h not in raw:raw[h]={r['start']:r for r in json.loads((folder/names[h]/'ghidra.json').read_text())}
 ins={r['rva']:r for r in raw[h][entry]['instructions']};terminals=[r[0] for r in db.execute("SELECT source FROM recovery_edge WHERE module=? AND entry=? AND kind='annotated_control_contract_requires_runtime'",(h,entry))]
 todo=collections.deque(pc+ins[pc]['length'] for pc in terminals if pc in ins and ins[pc]['flow']=='UNCONDITIONAL_CALL');seen=set()
 while todo:
  pc=todo.popleft()
  if pc in seen or pc not in ins:continue
  seen.add(pc);r=ins[pc];flow=r['flow']
  if 'JUMP' in flow:todo.extend(r['targets'])
  if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and not r['text'].startswith(('RET','UD2','HLT')):todo.append(pc+r['length'])
 assert set(c['only_ghidra'])<=seen,(h,entry,c['only_ghidra'],sorted(seen))
 disputes.append(dict(module=h,entry=entry,extra_addresses=c['only_ghidra'],classification='Independent ordinary fallthrough after explicitly annotated nonreturn calls; no byte disagreement.'))
for row in changes['resolved_nullable_arguments']:
 h,entry=row['module'],row['entry'];definition=row['definition'];ins={r['rva']:r for r in raw[h][entry]['instructions']};r=ins[definition['rva']]
 assert r['bytes']==definition['bytes'] and r['text'].startswith('XOR '),r
 assert row['current']['contract']=='cxa-throw-destructor' and row['current']['register']=='rdx'
runs={}
for suffix in ('boundary-inventory-v1','callback-zero-checks-v1','callback-zero-checks-v2','callback-zero-checks-v3','startup-recovery-v10-zero-guard','derived-bad-alloc-v1','ghidra-bad-alloc-v1','bad-alloc-control-check-v1','startup-recovery-v8','startup-recovery-v9-repeat','frontier-v8-delta-v1','callback-zero-delta-v1','ghidra-callback-zero-v1'):
 name='20260905-p3-'+suffix;p=root/'local/runs'/name;m=json.loads((p/'manifest.json').read_text());assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],elapsed_seconds=m['elapsed_seconds'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'))
report=dict(status='startup v9 evidence consistency pass; P3 gate open',current_directory=b.relative_to(root).as_posix(),reproducibility=repeat,summary=summary,derived_control=dict(path='local/cfg/bad-alloc-control-checked-v1/contracts.json',sha256=sha(root/'local/cfg/bad-alloc-control-checked-v1/contracts.json'),contracts=29,independent_instructions=265,previous_28_identical=True,new_contract=added[0]),retained_failures=[dict(run="20260905-p3-startup-v9-evidence-v1",reason="Audit used an incorrect literal callback contract ID. All independent byte/control checks passed before that assertion; corrected to the existing exact cxa-throw-destructor ID.")],callback_changes=changes,independent_disputes=disputes,ghidra_summary=ghidra,tests=33,third_guarded_recovery_identical=True,runs=runs,gate='P3 remains open: eight fence findings, 9029 indirect-call records, 430 indirect-jump records, 155 unknown callback arguments, mutable constructor tables and native callback/exception/service/control contracts remain unresolved. Compilation is distinct from execution.',native_game_boot=False,native_port_playable=False)
write_json(root/'reports/startup-v9-evidence.json',report)
print(json.dumps(dict(status=report['status'],entries=21160,instructions=873581,fence_findings=8,nullable_arguments=15,unknown_callback_arguments=155,ghidra_windows=10,extra_fallthrough_instructions=sum(len(x['extra_addresses']) for x in disputes))),flush=True)
