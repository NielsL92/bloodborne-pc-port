"""Cross-check callback closure bodies and exact mutable-slot operands independently."""
import collections,json,re,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();source=root/'local/cfg/startup-recovery-v12-relocations';delta=root/'local/cfg/callback-candidate-delta-v1';ghidra=root/'local/cfg/ghidra-callback-candidates-v1';out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);names=dict(db.execute('select hash,name from module'));comparisons=read(ghidra/'comparison.json');summary=read(ghidra/'summary.json')
assert summary['source_db_sha256']==sha(source/'analysis.sqlite')
selected={(r['module'],r['start']) for r in comparisons};assert selected=={(r['module'],r['start']) for r in read(delta/'selection.json')}
raw={};disputes=[]
for row in comparisons:
 h,entry=row['module'],row['start'];assert not row['boundary_disagreements'] and not row['only_recovery'],row
 if h not in raw:raw[h]={r['start']:{i['rva']:i for i in r['instructions']} for r in read(ghidra/names[h]/'ghidra.json')}
 ins=raw[h][entry];terminals=[r[0] for r in db.execute("select source from recovery_edge where module=? and entry=? and kind='annotated_control_contract_requires_runtime'",(h,entry))]
 todo=collections.deque(pc+ins[pc]['length'] for pc in terminals if pc in ins and ins[pc]['flow']=='UNCONDITIONAL_CALL');seen=set()
 while todo:
  pc=todo.popleft()
  if pc in seen or pc not in ins:continue
  seen.add(pc);r=ins[pc];flow=r['flow']
  if 'JUMP' in flow:todo.extend(r['targets'])
  if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and not r['text'].startswith(('RET','UD2','HLT')):todo.append(pc+r['length'])
 if row['only_ghidra']:
  record=dict(module=h,entry=entry,extra=row['only_ghidra'],unexplained=sorted(set(row['only_ghidra'])-seen));disputes.append(record)
  assert not record['unexplained'],record
slot_checks=[];constant_checks=[]
for row in read(delta/'records.json'):
 h,entry,pc=row['module'],row['entry'],row['source'];ins=raw[h][entry];detail=row['detail'];site=ins[pc]
 assert site['flow'] in ('UNCONDITIONAL_CALL','UNCONDITIONAL_JUMP'),row
 assert all(at in ins for at in detail['provenance'])
 if row['kind']=='callback_relocation_binding_unvalidated':
  origin=ins[detail['provenance'][0]];absolute=[int(x,16) for x in re.findall(r'\[0x([0-9a-fA-F]+)\]',origin['text'])]
  assert origin['text'].startswith('MOV ') and detail['slot'] in absolute,(origin,detail)
  slot_checks.append(dict(module=h,entry=entry,call=pc,slot=detail['slot'],independent_text=origin['text'],provenance=detail['provenance']))
 elif row['kind']=='callback_contract_target_candidate':
  origin=ins[detail['provenance'][0]]
  assert origin['text'].startswith(('LEA ','MOV ','XOR ','SUB ')),origin
  constant_checks.append(dict(module=h,entry=entry,call=pc,target=row['target'],independent_origin=origin['text'],provenance=[ins[at]['text'] for at in detail['provenance']]))
report=dict(status='independent callback candidate comparison passed; runtime binding remains unknown',source_db_sha256=sha(source/'analysis.sqlite'),selected_entries=len(selected),shared_instructions=summary['common_instructions'],ghidra_raw_sha256={names[h]:sha(ghidra/names[h]/'ghidra.json') for h in raw},comparison_sha256=sha(ghidra/'comparison.json'),slot_checks=slot_checks,constant_checks=constant_checks,explained_extra_reachability=disputes,unexplained=0,limitations='Independent SLEIGH bytes, flow and absolute slot operands. Conditional SysV preservation is an ABI assumption, not proof of callee execution. Relocation provider identity and mutable runtime binding remain separate. No game execution.')
write_json(out/'checked.json',report);print(json.dumps(dict(status=report['status'],entries=len(selected),shared=report['shared_instructions'],slot_checks=len(slot_checks),constant_checks=len(constant_checks),extra=sum(len(r['extra']) for r in disputes))),flush=True)
