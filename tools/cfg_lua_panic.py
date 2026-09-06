"""Load checked, scoped panic-field candidates without assuming runtime object identity."""
import json,struct
from pathlib import Path

def validate_candidate(r,images,is_code):
 h=r['module'];assert r['module_sha256']==h
 assert r['global_offset']==0x20 and r['field_offset']==0x50,'unsupported Lua field layout'
 assert r['conditions'] and r['limitations'],'conditional evidence required'
 owners={o['entry']:{i['rva']:i for i in o['instructions']} for o in r['owners']}
 assert len(owners)==len(r['owners']) and r['owner'] in owners
 for o in r['owners']:
  assert o['instructions'][0]['rva']==o['entry'],'owner mismatch'
  for i in o['instructions']:
   assert images[h].at_va(i['rva'],i['size']).hex()==i['bytes'],'Lua witness bytes changed'
 call=owners[r['owner']][r['site']];load=owners[r['owner']][r['global_load']]
 assert call['bytes']=='ff5050' and load['bytes']=='488b4720','wrong panic dispatch operands'
 assert load['rva']+load['size']==call['rva'],'noncontiguous global load'
 targets=[]
 for a in r['assignments']:
  own=owners[a['entry']];lea=own[a['lea']];store=own[a['store']]
  raw=bytes.fromhex(lea['bytes'])
  assert len(raw)==lea['size']==7 and raw[:3]==bytes.fromhex('488d0d'),'not RIP-relative RCX address'
  assert lea['rva']+7+struct.unpack('<i',raw[3:])[0]==a['target'],'stored target mismatch'
  assert store['bytes']=='48894850' and lea['rva']+7==store['rva'],'wrong or separated callback store'
  assert is_code(h,a['target']) and a['body'][0]['rva']==a['target'],'non-code or mismatched target'
  for i in a['body']:
   assert images[h].at_va(i['rva'],i['size']).hex()==i['bytes'],'Lua target bytes changed'
  assert a['body'][-1]['bytes']=='c3'
  targets.append(dict(target=a['target'],assignment_entry=a['entry'],assignment_site=a['store'],role=a['role'],conditions=r['conditions']))
 assert len({a['target'] for a in targets})==len(targets)
 return (h,r['owner'],r['site']),targets

def load_candidates(path,images,is_code):
 from tools.cfg_recover_startup import sha
 r=json.loads(Path(path).read_text(encoding='utf-8'));assert r['status']=='independent Lua panic field candidates passed'
 for p,digest in r['evidence'].items():assert sha(p)==digest,'Lua independent evidence changed'
 assert r['proposal_path'] in r['evidence']
 original=json.loads(Path(r['proposal_path']).read_text(encoding='utf-8'))
 for k,v in original.items():
  if k not in ('status','evidence'):assert r[k]==v,('Lua proposal field changed',k)
 for p,digest in original['evidence'].items():assert r['evidence'].get(p)==digest,'Lua public provenance changed'
 key,rows=validate_candidate(r,images,is_code);return {key:rows}
