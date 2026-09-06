"""Load independently checked symbol-based initial dispatch candidates, retaining unknowns."""
import collections,json
from pathlib import Path

def validate_candidate(r,images,links,relocs,is_code):
 h=r['module'];assert r['module_sha256']==h
 assert r['source_instructions'][0]['rva']==r['owner']
 assert any(i['rva']==r['site'] for i in r['source_instructions'])
 for i in r['source_instructions']+r['target_body']:
  assert images[h].at_va(i['rva'],i['size']).hex()==i['bytes'],'symbol dispatch witness bytes changed'
 assert len(r['chain'])==2 and r['chain'][0]['slot']==r['object_slot']
 for n,item in enumerate(r['chain']):
  slot=item['slot'];rel=item['relocation'];sym=item['symbol']
  assert relocs[h].get(slot)==rel and rel['type']==1 and rel['table']=='rela','symbol relocation changed'
  assert images[h].at_va(slot,8).hex()==item['raw_word'],'table cell changed'
  assert links[h]['symbols'][rel['symbol']]==sym and sym['defined'] and sym['type']==(1 if n==0 else 2),'symbol definition changed'
  keys=('nid','library','module')
  definitions=[(other,s['value']) for other,link in links.items() for s in link['symbols'] if s['defined'] and s['type']==sym['type'] and tuple(s[k] for k in keys)==tuple(sym[k] for k in keys)]
  assert definitions==[(h,sym['value'])],'ambiguous supplied symbol definition'
  assert item['initial_target']==sym['value']+rel['addend'] and 0<=item['initial_target']<1<<64
 assert r['chain'][1]['slot']==r['chain'][0]['initial_target']+r['table_offset']
 assert r['target']==r['chain'][1]['initial_target'] and is_code(h,r['target'])
 assert r['target_body'][0]['rva']==r['target']
 return (h,r['owner'],r['site']),r

def load_candidates(path,images,links,relocs,is_code):
 from tools.cfg_recover_startup import sha
 r=json.loads(Path(path).read_text(encoding='utf-8'));assert r['status']=='independent RTTI symbol-dispatch candidate passed'
 for p,digest in r['evidence'].items():assert sha(p)==digest,'symbol dispatch independent evidence changed'
 original=json.loads(Path(r['proposal_path']).read_text(encoding='utf-8'))
 assert r['proposal_path'] in r['evidence']
 for k,v in original.items():
  if k!='status':assert r[k]==v,('proposal field changed',k)
 for table in r['raw_tables'].values():assert sha(table['path'])==table['sha256']
 key,row=validate_candidate(r,images,links,relocs,is_code);return {key:[row]}
