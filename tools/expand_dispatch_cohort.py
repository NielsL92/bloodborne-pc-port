"""Apply independently checked cohort candidates without closing runtime calls."""
import argparse,copy,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('object_proof',type=Path);p.add_argument('cohort_proof',type=Path);p.add_argument('out',type=Path);p.add_argument('--template',default='constructed-singleton-slot-20',choices=['constructed-singleton-slot-20','constructed-subobject-slot-20']);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 def read(p):return json.loads(p.read_text(encoding='utf-8'))
 proof=read(a.object_proof);cohort=read(a.cohort_proof);assert proof['status']=='independent object dispatch candidates passed' and cohort['status']=='independent constructor dispatch cohort passed'
 template=next(r for r in proof['proposals'] if r['name']==a.template)
 expected={'constructed-singleton-slot-20':(0x53b3060,0x53b3080,0x2082ee0,0x5540670,0x2ba2b10,0),'constructed-subobject-slot-20':(0x53b2e70,0x53b2e90,0x207cb70,0x5540668,0x207bbf0,0x458)}[a.template]
 table,slot,target,cache,factory,offset=expected;assert (template['table'],template['slot'],template['target'],template['object_offset'])==(table,slot,target,offset)
 cohort_digest=sha(a.cohort_proof)
 keys={(r['module'],r['call_entry'],r['call']) for r in proof['proposals']};added=0
 for row in cohort['records']:
  assert row['module']==template['module'] and row['cache_slot']==cache and row['factory']==factory and row['offset']==template['offset'] and row.get('object_offset',0)==offset
  key=row['module'],row['entry'],row['site']
  if key in keys:continue
  candidate=copy.deepcopy(template);candidate.update(name=a.template+'-cohort',call_entry=row['entry'],call=row['site'],conditional=row['condition'],cohort_evidence_sha256=cohort_digest,cohort_start=row['start'])
  proof['proposals'].append(candidate);proof['witnesses'].append(dict(module=row['module'],entry=row['entry'],instructions=row['instructions']));keys.add(key);added+=1
 proof['proposals'].sort(key=lambda r:(r['module'],r['call_entry'],r['call'],r['slot']))
 proof.setdefault('cohort_expansions',[]).append(dict(template=a.template,object_proof_sha256=sha(a.object_proof),cohort_proof_sha256=sha(a.cohort_proof),cohort_windows=cohort['windows'],added_site_candidates=added,other_shapes=cohort['inventory']['other_shapes'],limitations=cohort['limitations']))
 write_json(a.out/'checked.json',proof);print(json.dumps(dict(status=proof['status'],proposals=len(proof['proposals']),added=added,cohort_windows=cohort['windows'],unique_targets=len({(r['module'],r['target']) for r in proof['proposals']}))),flush=True)
if __name__=='__main__':main()
