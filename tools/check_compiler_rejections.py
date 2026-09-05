"""Check the complete rejected-instruction census against independent Ghidra flow."""
import collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();source=root/'local/cfg/startup-recovery-v9-repeat';folder=root/'local/cfg/ghidra-compiler-rejections-v1';inspection=root/'local/compiler-spike/startup-rejection-inspection-v1'
db=sqlite3.connect(f'{(source/"analysis.sqlite").as_uri()}?mode=ro',uri=True);names=dict(db.execute('SELECT hash,name FROM module'));raw={};disputes=[]
summary=json.loads((folder/'summary.json').read_text());assert summary['entries']==48 and summary['common_instructions']==14595 and summary['boundary_disagreements']==0
for c in json.loads((folder/'comparison.json').read_text()):
 h,entry=c['module'],c['start'];assert not c['only_recovery']
 if h not in raw:raw[h]={r['start']:r for r in json.loads((folder/names[h]/'ghidra.json').read_text())}
 ins={r['rva']:r for r in raw[h][entry]['instructions']};terminals=[r[0] for r in db.execute("SELECT source FROM recovery_edge WHERE module=? AND entry=? AND kind='annotated_control_contract_requires_runtime'",(h,entry))]
 todo=collections.deque(pc+ins[pc]['length'] for pc in terminals if pc in ins and ins[pc]['flow']=='UNCONDITIONAL_CALL');seen=set()
 while todo:
  pc=todo.popleft()
  if pc in seen or pc not in ins:continue
  seen.add(pc);r=ins[pc];flow=r['flow']
  if 'JUMP' in flow:todo.extend(r['targets'])
  if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and not r['text'].startswith(('RET','UD2','HLT')):todo.append(pc+r['length'])
 if c['only_ghidra']:disputes.append(dict(module=h,entry=entry,extra=c['only_ghidra'],explained_after_nonreturn=sorted(set(c['only_ghidra'])&seen),unresolved=sorted(set(c['only_ghidra'])-seen)))
problems=json.loads((inspection/'problems.json').read_text())
for problem in problems:
 for owner in problem['owners']:
  ins={r['rva']:r for r in raw[owner['module']][owner['entry']]['instructions']};assert ins[owner['rva']]['bytes']==problem['bytes']
report=dict(status='independent rejected-instruction identities pass; extra reachability retained',ghidra_summary=summary,ghidra_comparison_sha256=sha(folder/'comparison.json'),problem_count=len(problems),problems_sha256=sha(inspection/'problems.json'),inspector_summary=json.loads((inspection/'summary.json').read_text()),independent_raw_sha256={names[h]:sha(folder/names[h]/'ghidra.json') for h in raw},reachability_differences=disputes,unexplained_extra_instructions=sum(len(r['unresolved']) for r in disputes),execution='none',limitations='All rejected instruction identities agree independently. Extra reachability is distinct from missing or unsupported semantics; annotations do not implement native services or runtime exceptions.')
write_json(root/'reports/compiler-rejections-evidence.json',report)
print(json.dumps(dict(status=report['status'],instructions=14595,problem_sites=len(problems),extra_instructions=sum(len(r['extra']) for r in disputes),unexplained=report['unexplained_extra_instructions'])),flush=True)
