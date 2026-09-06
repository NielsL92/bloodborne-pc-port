"""Reconcile independent Ghidra windows against exact decoded instruction manifests."""
import argparse,collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('selection',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 def read(p):return json.loads(p.read_text(encoding='utf-8'))
 con=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);names=dict(con.execute('select hash,name from module'));rows=read(a.ghidra/'comparison.json');raw={};disputes=[]
 assert {(r['module'],r['start']) for r in rows}=={(r['module'],r['start']) for r in read(a.selection)}
 assert read(a.ghidra/'summary.json')['source_db_sha256']==sha(a.source/'analysis.sqlite')
 for r in rows:
  assert not r['boundary_disagreements'] and not r['only_recovery'],r
  h,entry=r['module'],r['start']
  if h not in raw:raw[h]={w['start']:{i['rva']:i for i in w['instructions']} for w in read(a.ghidra/names[h]/'ghidra.json')}
  ins=raw[h][entry];terminals=[pc for pc, in con.execute("select source from recovery_edge where module=? and entry=? and kind='annotated_control_contract_requires_runtime'",(h,entry))]
  todo=collections.deque(pc+ins[pc]['length'] for pc in terminals if pc in ins and ins[pc]['flow']=='UNCONDITIONAL_CALL');seen=set()
  while todo:
   pc=todo.popleft()
   if pc in seen or pc not in ins:continue
   seen.add(pc);i=ins[pc];flow=i['flow']
   if 'JUMP' in flow:todo.extend(i['targets'])
   if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and not i['text'].startswith(('RET','UD2','HLT')):todo.append(pc+i['length'])
  if r['only_ghidra']:
   assert set(r['only_ghidra'])<=seen,r;disputes.append(dict(module=h,entry=entry,extra=r['only_ghidra'],classification='ordinary fallthrough after existing annotated nonreturn calls'))
 report=dict(status='independent window closure comparison passed',source_db_sha256=sha(a.source/'analysis.sqlite'),selection_sha256=sha(a.selection),comparison_sha256=sha(a.ghidra/'comparison.json'),windows=len(rows),shared_instructions=sum(r['common_instructions'] for r in rows),raw_sha256={names[h]:sha(a.ghidra/names[h]/'ghidra.json') for h in raw},explained_extra=disputes,unexplained=0,limitations='Instruction identities and bounded reachability only. Metadata roots and nonreturn contracts do not implement native execution or establish whole-function bounds.')
 write_json(a.out/'checked.json',report);print(json.dumps(dict(status=report['status'],windows=report['windows'],shared=report['shared_instructions'],extra=sum(len(r['extra']) for r in disputes))),flush=True)
if __name__=='__main__':main()
