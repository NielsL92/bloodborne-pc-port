"""Check the finite cache/factory dispatch pattern using independent SLEIGH operands."""
import argparse,hashlib,json,re
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json

def match_window(rows):
 if len(rows)!=12 or any(x['rva']+x['length']!=y['rva'] for x,y in zip(rows,rows[1:])):return None
 text=[r['text'] for r in rows]
 lea=re.fullmatch(r'LEA (R12|R13|R14|R15|RBX|RBP),\[0x([0-9a-fA-F]+)\]',text[0])
 if not lea:return None
 cache,slot=lea[1],int(lea[2],16)
 load=re.fullmatch(r'MOV (RBX|RBP|R12|R13|R14|R15),qword ptr \['+cache+r'\]',text[1])
 if not load:return None
 obj=load[1]
 if obj==cache:return None
 if text[2]!='TEST '+obj+','+obj:return None
 if rows[3]['flow']!='CONDITIONAL_JUMP' or rows[3]['targets']!=[rows[7]['rva']] or not text[3].startswith('JNZ '):return None
 if rows[4]['flow']!='UNCONDITIONAL_CALL' or rows[4]['targets']!=[0x2ba2b10]:return None
 if text[5]!='MOV '+obj+',RAX' or text[6]!='MOV qword ptr ['+cache+'],'+obj:return None
 if text[7]!='MOV RAX,qword ptr ['+obj+']':return None
 if not re.fullmatch(r'LEA RDI,\[RSP(?: \+ 0x[0-9a-fA-F]+)?\]',text[8]):return None
 if text[9]!='XOR EDX,EDX' or text[10]!='MOV RSI,'+obj or text[11]!='CALL qword ptr [RAX + 0x20]':return None
 if rows[11]['flow']!='COMPUTED_CALL':return None
 return dict(cache_slot=slot,factory=rows[4]['targets'][0],offset=0x20,registers=dict(cache=cache.lower(),object=obj.lower(),table='rax'))

def match_subobject_window(rows):
 if len(rows) not in (13,14) or any(x['rva']+x['length']!=y['rva'] for x,y in zip(rows,rows[1:])):return None
 text=[r['text'] for r in rows];lea=re.fullmatch(r'LEA (RAX|R12|R13|R14|R15|RBX|RBP),\[0x([0-9a-fA-F]+)\]',text[0])
 if not lea:return None
 cache,slot=lea[1],int(lea[2],16);load=re.fullmatch(r'MOV (RBX|RBP|R12|R13|R14|R15),qword ptr \['+cache+r'\]',text[1])
 if not load:return None
 obj=load[1];table_index=9 if len(rows)==14 else 8
 if obj==cache or text[2]!='TEST '+obj+','+obj:return None
 if rows[3]['flow']!='CONDITIONAL_JUMP' or rows[3]['targets']!=[rows[table_index]['rva']] or not text[3].startswith('JNZ '):return None
 if rows[4]['flow']!='UNCONDITIONAL_CALL' or rows[4]['targets']!=[0x207bbf0]:return None
 if text[5]!='MOV '+obj+',RAX' or text[6]!='ADD '+obj+',0x458':return None
 if len(rows)==14:
  reload=re.fullmatch(r'LEA '+cache+r',\[0x([0-9a-fA-F]+)\]',text[7])
  if not reload or int(reload[1],16)!=slot:return None
 elif cache=='RAX':return None
 if text[table_index-1]!='MOV qword ptr ['+cache+'],'+obj or text[table_index]!='MOV RAX,qword ptr ['+obj+']':return None
 if not re.fullmatch(r'LEA RDI,\[RSP(?: \+ 0x[0-9a-fA-F]+)?\]',text[table_index+1]):return None
 if text[-3]!='XOR EDX,EDX' or text[-2]!='MOV RSI,'+obj or text[-1]!='CALL qword ptr [RAX + 0x20]' or rows[-1]['flow']!='COMPUTED_CALL':return None
 return dict(cache_slot=slot,factory=0x207bbf0,offset=0x20,object_offset=0x458,registers=dict(cache=cache.lower(),object=obj.lower(),table='rax'))

def match_cached_tail(rows):
 if len(rows) not in (11,12) or any(x['rva']+x['length']!=y['rva'] for x,y in zip(rows,rows[1:])):return None
 text=[r['text'] for r in rows];load=re.fullmatch(r'MOV (RBX|RBP|R12|R13|R14|R15),qword ptr \[(RBX|RBP|R12|R13|R14|R15)\]',text[0])
 if not load:return None
 obj,cache=load[1],load[2];offset=0x458 if len(rows)==12 else 0;factory=0x207bbf0 if offset else 0x2ba2b10;table_index=7 if offset else 6
 if obj==cache or text[1]!='TEST '+obj+','+obj:return None
 if not text[2].startswith('JNZ ') or rows[2]['flow']!='CONDITIONAL_JUMP' or rows[2]['targets']!=[rows[table_index]['rva']]:return None
 if rows[3]['flow']!='UNCONDITIONAL_CALL' or rows[3]['targets']!=[factory] or text[4]!='MOV '+obj+',RAX':return None
 if offset and text[5]!='ADD '+obj+',0x458':return None
 if text[table_index-1]!='MOV qword ptr ['+cache+'],'+obj or text[table_index]!='MOV RAX,qword ptr ['+obj+']':return None
 if not re.fullmatch(r'LEA RDI,\[RSP(?: \+ 0x[0-9a-fA-F]+)?\]',text[table_index+1]):return None
 if text[-3]!='XOR EDX,EDX' or text[-2]!='MOV RSI,'+obj or text[-1]!='CALL qword ptr [RAX + 0x20]' or rows[-1]['flow']!='COMPUTED_CALL':return None
 return dict(cache_register=cache.lower(),object_register=obj.lower(),factory=factory,object_offset=offset,table_slot_offset=0x20,load_site=rows[0]['rva'],dispatch_site=rows[-1]['rva'])

def main():
 p=argparse.ArgumentParser();p.add_argument('cohort',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 def read(p):return json.loads(p.read_text(encoding='utf-8'))
 inventory=read(a.cohort/'summary.json');rows=read(a.cohort/'matches.json');summary=read(a.ghidra/'summary.json');assert inventory['source_db_sha256']==summary['source_db_sha256'] and summary['requests_sha256']==sha(a.cohort/'matches.json')
 raw={}
 for m in summary['modules']:
  for w in read(a.ghidra/m['name']/'ghidra.json'):raw[m['module'],w['start']]=w
 assert set(raw)=={(r['module'],r['start']) for r in rows}
 for row in rows:
  window=raw[row['module'],row['start']];assert window['end']==row['end'];ins=window['instructions']
  assert [(r['rva'],r['length'],r['bytes']) for r in ins]==[(r['pc'],r['size'],r['bytes']) for r in row['instructions']]
  got=(match_subobject_window(ins) if row.get('object_offset')==0x458 else match_window(ins));assert got is not None,(row['site'],ins)
  assert got=={k:row[k] for k in got},(got,row)
  assert hashlib.sha256(b''.join(bytes.fromhex(r['bytes']) for r in ins)).hexdigest()==row['instruction_bytes_sha256']
 report=dict(status='independent constructor dispatch cohort passed',source_db_sha256=inventory['source_db_sha256'],matches_sha256=sha(a.cohort/'matches.json'),other_sites_sha256=sha(a.cohort/'other-sites.json'),ghidra_summary_sha256=sha(a.ghidra/'summary.json'),windows=len(rows),shared_instructions=sum(len(r['instructions']) for r in rows),inventory=inventory,records=rows,limitations='Conditional initial-object candidates only. Calls and mutable cache/table bindings remain unresolved. A pattern match does not prove all incoming states or successful native construction; no execution coverage.')
 write_json(a.out/'checked.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('records','inventory')}),flush=True)
if __name__=='__main__':main()
