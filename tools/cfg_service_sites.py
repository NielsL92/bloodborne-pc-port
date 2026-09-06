"""Exact, independently checked service-call annotations; never global service summaries."""
import json
from pathlib import Path
from tools.startup_service_inventory import SPECS

def validate_site(row,images,imported,pads):
 from tools.cfg_recover_startup import sha
 expected=next((s for s in SPECS if s['id']==row['id']),None)
 assert expected,'unknown service-site policy'
 for k,v in expected.items():assert row[k]==v,('service policy changed',k)
 h,e,pc=row['module'],row['entry'],row['site']
 assert row['instructions'] and row['instructions'][0][0]==e
 for at,size,raw in row['instructions']:
  assert images[h].at_va(at,size).hex()==raw,'service witness bytes changed'
 call=next(x for x in row['instructions'] if x[0]==pc)
 assert row['independent']['call']['bytes']==call[2]
 assert row['independent']['call']['targets']==[row['target']]
 assert row['independent']['call']['flow']=='UNCONDITIONAL_CALL'
 imp=imported(h,row['target'])
 assert imp and [imp[k] for k in ('nid','library','module')]==row['import_key']==[row['nid'],'libkernel','libkernel'],'service import binding changed'
 if row['context']:
  assert not pads.get((h,e),[]),'new entry path invalidates contextual arguments'
 return (h,e,pc),row

def load_sites(path,images,imported,pads):
 from tools.cfg_recover_startup import sha
 data=json.loads(Path(path).read_text())
 assert data['status']=='independent Ghidra service-site comparison passed'
 assert data['base_contracts_sha256']==sha('tools/cfg_import_contracts.json')
 for p,digest in data['evidence'].items():assert sha(p)==digest,'independent evidence changed'
 for p,digest in data['references'].items():assert sha(p)==digest,'reference identity changed'
 assert len(data['contracts'])==len(SPECS)
 result={}
 for row in data['contracts']:
  key,value=validate_site(row,images,imported,pads)
  assert key not in result,'duplicate service-site contract'
  result[key]=value
 return result

def match_site(sites,module,entry,site,target,imp):
 row=sites.get((module,entry,site))
 if row is None:return None
 assert target==row['target'] and imp and [imp[k] for k in ('nid','library','module')]==row['import_key'],'service-site transfer changed'
 return row
