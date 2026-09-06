"""Independently prove conditional ordinary-return paths, preserving unknown transfers."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.cfg_conditional_control import independent_paths
from tools.conditional_control_inventory import CALLBACKS
p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
r=read(a.proposal/'proposal.json');summary=read(a.ghidra/'summary.json');assert summary['source_db_sha256']==r['source_db_sha256'] and summary['exception_roots_supplied']
raw={};units={(u['module_sha256'],u['entry']):u for u in r['units']};independent=[]
assert {(s['module'],s['start']) for s in read(a.ghidra/'selection.json')}==set(units)
for (h,e),u in units.items():
 name=u['module']
 if h not in raw:raw[h]={w['start']:w for w in read(a.ghidra/name/'ghidra.json')}
 w=raw[h][e];actual={i['rva']:i for i in w['instructions']}
 assert [e]+next(s['additional_roots'] for s in read(a.ghidra/'selection.json') if s['module']==h and s['start']==e)==u['roots']
 for i in u['instructions']:assert (i['size'],i['bytes'])==(actual[i['rva']]['length'],actual[i['rva']]['bytes'])
for p in r['proofs']:
 h,e=p['module'],p['entry'];u=units[h,e];w=raw[h][e];actual={i['rva']:i for i in w['instructions']};terms={int(pc) for pc in p['terminals']}
 visited=independent_paths(w['instructions'],p['roots'],terms,CALLBACKS.get((h,e),{}));assert visited==p['visited']
 terminals=[]
 for pc in sorted(terms):
  target=actual[pc]['targets'][0]
  assert any(x['source']==pc and x['target']==target and x['kind'] in ('direct_call','cross_fence_jump','import_contract_unvalidated') for x in u['edges'])
  terminals.append(dict(site=pc,target=target,contracts=p['terminals'][str(pc)],independent=actual[pc]))
 independent.append(dict(id=p['id'],visited=visited,terminals=terminals,extra_instructions=sorted(set(actual)-set(visited)),callback_forms=[actual[pc] for pc in CALLBACKS.get((h,e),{})]))
for s in r['sites']:
 actual=next(i for i in raw[s['module']][s['entry']]['instructions'] if i['rva']==s['site']);assert actual['flow']=='UNCONDITIONAL_CALL' and actual['targets']==[s['target']];s['independent']=actual
r.update(status='independent conditional callback-control comparison passed',proposal_path=str(a.proposal/'proposal.json'),independent_proofs=independent,shared_instructions=sum(len(u['instructions']) for u in r['units']))
for f in [a.proposal/'proposal.json',a.proposal/'selection.json',a.ghidra/'summary.json',a.ghidra/'selection.json',a.ghidra/'comparison.json']+[a.ghidra/u['module']/'ghidra.json' for u in r['units']]:r['evidence'][str(f)]=sha(f)
write_json(a.out/'checked.json',r);print(json.dumps(dict(status=r['status'],helpers=len(independent),sites=len(r['sites']),shared=r['shared_instructions'],unknown_callback_sites=sum(len(p['callbacks']) for p in r['proofs']))))
