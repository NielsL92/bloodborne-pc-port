"""Checked conditional control at exactly five disputed sites; no global policy relaxation."""
import json,struct
from pathlib import Path
from tools.cfg_derive_control import prove
from tools.conditional_control_inventory import HELPERS,CALLBACKS,SITES,CONDITIONS,model

def independent_paths(instructions,roots,terminals,approved):
 ins={i['rva']:i for i in instructions};assert len(ins)==len(instructions);nodes={}
 for pc,i in ins.items():
  flow=i['flow']
  if pc in approved:
   assert flow=='COMPUTED_CALL' and i['bytes']==approved[pc],'wrong conditional callback form'
   nodes[pc]=[pc+i['length']]
  elif 'COMPUTED' in flow or 'TERMINATOR' in flow:nodes[pc]=None
  elif 'JUMP' in flow:nodes[pc]=i['targets']+([] if flow=='UNCONDITIONAL_JUMP' else [pc+i['length']])
  else:nodes[pc]=[pc+i['length']]
 for pc in terminals:
  assert pc in ins and ins[pc]['flow'] in ('UNCONDITIONAL_CALL','UNCONDITIONAL_JUMP') and len(ins[pc]['targets'])==1,'invalid terminal form'
 assert not set(approved)&set(terminals),'callback is not a no-return terminal'
 visited=prove(nodes,roots,set(terminals))
 if visited is not None:assert set(approved)<=set(visited),'unvisited callback obligation'
 return visited

def validate_sites(r,images,imported,pads):
 from tools.cfg_recover_startup import sha
 base=json.loads(Path('tools/cfg_import_contracts.json').read_text(encoding='utf-8'))
 assert r['base_contracts_sha256']==sha('tools/cfg_import_contracts.json') and r['base_contracts']==base
 assert r['conditions']==CONDITIONS and r['limitations'],'conditional control policy changed'
 units={(u['module_sha256'],u['entry']):u for u in r['units']}
 assert set(units)==set(HELPERS)|{(h,e) for h,e,pc,t in SITES}
 for (h,e),u in units.items():
  assert u['roots']==[e]+pads.get((h,e),[]),'exception roots changed'
  for i in u['instructions']:assert images[h].at_va(i['rva'],i['size']).hex()==i['bytes'],'conditional-control witness bytes changed'
 local={(e['module_sha256'],e['rva']):[c['id']] for c in base['contracts'] for e in c.get('local_entries',[])};imports={tuple(c[k] for k in ('nid','library','module')):[c['id']] for c in base['contracts']};known_ids={c['id'] for c in base['contracts']};proofs={}
 assert {(p['module'],p['entry']) for p in r['proofs']}==set(HELPERS)
 independent={p['id']:p for p in r['independent_proofs']}
 for p in r['proofs']:
  h,e=p['module'],p['entry'];u=units[h,e];nodes,terms,ev=model(u,local,imports,True);visited=prove(nodes,u['roots'],terms)
  assert visited==p['visited']==[i['rva'] for i in u['instructions']]
  assert p['terminals']=={str(pc):ev[pc] for pc in visited if pc in terms}
  assert p['dependencies']==sorted({c for cs in p['terminals'].values() for c in cs}) and set(p['dependencies'])<=known_ids,'unverified transitive dependency'
  assert p['callbacks']==[dict(site=pc,bytes=b,obligation=CONDITIONS[0]) for pc,b in CALLBACKS.get((h,e),{}).items()]
  independent_terminals=independent[p['id']]['terminals'];assert {x['site'] for x in independent_terminals}==terms
  for t in independent_terminals:
   witness=next(i for i in u['instructions'] if i['rva']==t['site']);raw=bytes.fromhex(witness['bytes'])
   assert len(raw)==5 and raw[0]==0xe8 and t['site']+5+struct.unpack('<i',raw[1:])[0]==t['target'],'terminal instruction target changed'
   candidates=set(local.get((h,t['target']),[]));imp=imported(h,t['target'])
   if imp:candidates.update(imports.get(tuple(imp[k] for k in ('nid','library','module')),[]))
   assert candidates==set(p['terminals'][str(t['site'])]),'terminal binding changed'
  proofs[h,e]=p;local[h,e]=[p['id']];known_ids.add(p['id'])
 assert {(x['module'],x['entry'],x['site'],x['target']) for x in r['sites']}==set(SITES) and len(r['sites'])==len(SITES)
 result={}
 for s in r['sites']:
  h,e,pc,target=s['module'],s['entry'],s['site'],s['target'];assert s['proof_id']==proofs[h,target]['id']
  assert s['id']=='disputed-ending-'+h[:12]+'-'+format(e,'x')
  assert any(i['rva']==pc and i['mnemonic']=='call' for i in units[h,e]['decoded'])
  assert s['independent']['flow']=='UNCONDITIONAL_CALL' and s['independent']['targets']==[target]
  result[h,e,pc]=s|dict(conditions=r['conditions'])
 return result

def load_sites(path,images,imported,pads):
 from tools.cfg_recover_startup import sha
 r=json.loads(Path(path).read_text(encoding='utf-8'));assert r['status']=='independent conditional callback-control comparison passed'
 for p,digest in r['evidence'].items():assert sha(p)==digest,'conditional-control evidence changed'
 assert r['proposal_path'] in r['evidence'];old=json.loads(Path(r['proposal_path']).read_text(encoding='utf-8'))
 for k,v in old.items():
  if k not in ('status','evidence','sites'):assert r[k]==v,('conditional proposal changed',k)
 assert [{k:v for k,v in s.items() if k!='independent'} for s in r['sites']]==old['sites']
 for p,digest in old['evidence'].items():assert r['evidence'].get(p)==digest
 return validate_sites(r,images,imported,pads)

def match_site(sites,module,entry,site,target):
 row=sites.get((module,entry,site))
 if row is not None:assert row['target']==target,'conditional ending target changed'
 return row
