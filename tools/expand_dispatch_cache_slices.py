"""Expand checked noncontiguous cache provenance while retaining unknown dispatch."""
import argparse,copy,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('object_proof',type=Path);p.add_argument('cache_proof',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
proof=read(a.object_proof);slices=read(a.cache_proof);assert proof['status']=='independent object dispatch candidates passed' and slices['status']=='independent dispatch cache slices passed'
templates={r['name']:r for r in proof['proposals'] if r['name'] in ('constructed-singleton-slot-20','constructed-subobject-slot-20')};keys={(r['module'],r['call_entry'],r['call']) for r in proof['proposals']};digest=sha(a.cache_proof);added=[];unknown=[]
for row in slices['records']:
 if not row['complete']:unknown.append(dict(module=row['module'],entry=row['entry'],site=row['tail']['dispatch_site'],failures=row['failures']));continue
 assert row['independent']['complete'] and not row['failures'] and row['targets']==row['independent']['targets'] and len(row['targets'])==1 and row['targets'][0]['kind']=='module-rva'
 tail=row['tail'];cache=row['targets'][0]['value'];key=row['module'],row['entry'],tail['dispatch_site'];assert key not in keys
 name='constructed-singleton-slot-20' if cache==0x5540670 else 'constructed-subobject-slot-20';template=templates[name]
 assert (cache,tail['factory'],tail['object_offset']) in [(0x5540670,0x2ba2b10,0),(0x5540668,0x207bbf0,0x458)] and tail['object_offset']==template['object_offset']
 candidate=copy.deepcopy(template);candidate.update(name=name+'-earlier-cache-slice',call_entry=row['entry'],call=tail['dispatch_site'],conditional='Only the checked factory initial object/subobject with an unchanged cache and table. Earlier cache address is independently sliced under normal SysV saved-register return assumptions; native binding, mutation and initialization remain unknown.',cache_slice_evidence_sha256=digest,cache_slice_site=row['site'],conditional_normal_sysv_returns=row['conditional_normal_sysv_returns'])
 proof['proposals'].append(candidate);proof['witnesses'].append(dict(module=row['module'],entry=row['entry'],instructions=row['source_instructions']));keys.add(key);added.append(dict(module=key[0],entry=key[1],site=key[2],cache=cache,target=candidate['target']))
proof['proposals'].sort(key=lambda r:(r['module'],r['call_entry'],r['call'],r['slot']));proof['cache_slice_expansion']=dict(object_proof_sha256=sha(a.object_proof),cache_proof_sha256=digest,added=added,unknown=unknown)
write_json(a.out/'checked.json',proof);write_json(a.out/'summary.json',dict(status=proof['status'],proposals=len(proof['proposals']),added=len(added),unknown=len(unknown),cache_proof_sha256=digest));print(json.dumps(read(a.out/'summary.json')),flush=True)
