"""Check narrowly scoped service contracts against independent SLEIGH flow and bytes."""
import argparse,json,re,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.startup_service_inventory import SPECS

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('inventory',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False)
 data=json.loads(a.inventory.read_text());gsummary=json.loads((a.ghidra/'summary.json').read_text())
 assert data['source_db_sha256']==gsummary['source_db_sha256']==sha(a.source/'analysis.sqlite')
 assert data['source_manifest_sha256']==sha(a.source/'compilation-manifest.jsonl')
 assert gsummary['exception_roots_supplied']
 db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 names=dict(db.execute('SELECT hash,name FROM module'));raw={};checks=[]
 for h in sorted({c['module'] for c in data['cases']}):
  raw[h]={r['start']:r for r in json.loads((a.ghidra/names[h]/'ghidra.json').read_text())}
 comparisons=json.loads((a.ghidra/'comparison.json').read_text())
 assert len(comparisons)==len(data['cases'])==11
 for case in data['cases']:
  h,e=case['module'],case['entry'];comp=next(c for c in comparisons if (c['module'],c['start'])==(h,e))
  assert not comp['boundary_disagreements'] and not comp['only_recovery'],comp
  ins={i['rva']:i for i in raw[h][e]['instructions']}
  for i in case['instructions']:assert (i['size'],i['bytes'])==(ins[i['rva']]['length'],ins[i['rva']]['bytes'])
  # Retain all extra independently reached instructions: no silent normalization.
  checks.append(dict(module=h,entry=e,shared=len(case['instructions']),only_ghidra=comp['only_ghidra']))
 contracts=[]
 for row in data['contracts']:
  expected=next(s for s in SPECS if s['id']==row['id'])
  for k,v in expected.items():assert row[k]==v,(k,row[k],v)
  h,e,pc=row['module'],row['entry'],row['site'];ins={i['rva']:i for i in raw[h][e]['instructions']}
  assert ins[pc]['flow']=='UNCONDITIONAL_CALL' and ins[pc]['targets']==[row['target']]
  if row['context']:
   assert not db.execute('SELECT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL',(h,e)).fetchall()
   path=[];at=e
   while at!=pc:
    i=ins[at];assert i['flow']=='FALL_THROUGH',i
    path.append(at);at+=i['length'];assert at<=pc
   assert path==[0x1f560,0x1f561,0x1f564,0x1f569]
   # Independently printed SLEIGH operands and write destinations, not a Capstone re-decode.
   mov=ins[0x1f564];zero=ins[0x1f569]
   assert re.sub(r'\s+','',mov['text']).upper()=='MOVEDI,0XA002000B',mov
   assert re.sub(r'\s+','',zero['text']).upper()=='XORESI,ESI',zero
   assert 'EDI' in mov['written_registers'] or 'RDI' in mov['written_registers']
   assert 'ESI' in zero['written_registers'] or 'RSI' in zero['written_registers']
  row=dict(row,independent=dict(call=ins[pc],context=[ins[x] for x in row['context_instructions']]))
  contracts.append(row)
 evidence={str(a.inventory):sha(a.inventory),str(a.ghidra/'comparison.json'):sha(a.ghidra/'comparison.json'),str(a.ghidra/'summary.json'):sha(a.ghidra/'summary.json')}
 evidence.update({str(a.ghidra/names[h]/'ghidra.json'):sha(a.ghidra/names[h]/'ghidra.json') for h in raw})
 result=dict(schema=1,status='independent Ghidra service-site comparison passed',source_db_sha256=data['source_db_sha256'],base_contracts_sha256=sha('tools/cfg_import_contracts.json'),references=data['references'],evidence=evidence,contracts=contracts,checks=checks,
  retained_quarantines=[dict(module=c['module'],entry=c['entry'],issues=c['issues']) for c in data['cases'] if c['issues'] and not any((c['module'],c['entry'])==(r['module'],r['entry']) for r in contracts)],limitations=data['limitations'])
 write_json(a.out/'contracts.json',result)
 print(json.dumps(dict(status=result['status'],contracts=len(contracts),checked_windows=len(checks),shared_instructions=sum(c['shared'] for c in checks),ghidra_extra_instructions=sum(len(c['only_ghidra']) for c in checks),retained_quarantines=len(result['retained_quarantines']))))
if __name__=='__main__':main()
