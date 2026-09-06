"""Compare independent symbol records, SLEIGH operand provenance and the new RTTI body."""
import argparse,json,re
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('symbols',type=Path);p.add_argument('windows',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
r=read(a.proposal/'proposal.json');s=read(a.symbols/'dispatch.json');w=read(a.windows/'summary.json');raw=read(a.windows/'libc.prx/ghidra.json')
assert w['source_db_sha256']==r['source_db_sha256'] and w['requests_sha256']==sha(a.proposal/'windows.json')
for expected,actual in zip(r['chain'],s['chain'],strict=True):
 rel=expected['relocation'];sym=expected['symbol']
 assert actual['slot']==expected['slot'] and actual['raw_word']==int.from_bytes(bytes.fromhex(expected['raw_word']),'little')
 assert (actual['relocation_type'],actual['symbol_index'],actual['addend'])==(rel['type'],rel['symbol'],rel['addend'])
 for key in ('name','bind','value','size'):assert actual[key]==sym[key]
 assert actual['symbol_type']==sym['type'] and actual['section_index']!=0 and actual['initial_target']==expected['initial_target']
 assert actual['symbol_byte_offset']==sym['index']*24
assert s['target']==r['target'] and s['chain'][1]['slot']==s['chain'][0]['initial_target']+r['table_offset']
owner={i['rva']:i for x in raw if x['start']==r['owner'] for i in x['instructions']}
for i in r['source_instructions']:assert (i['size'],i['bytes'])==(owner[i['rva']]['length'],owner[i['rva']]['bytes'])
expected_source={i['rva'] for i in r['source_instructions']};assert set(owner)==expected_source,'unexplained independent owner reachability difference'
lea=owner[0x607fd];load=owner[0x60804];call=owner[r['site']]
match=re.fullmatch(r'LEA RCX,\[0x([0-9a-fA-F]+)\]',lea['text']);assert match and int(match[1],16)==r['object_slot']
assert load['text']=='MOV RCX,qword ptr [RCX]'
assert call['text']=='CALL qword ptr [RCX + 0x10]' and call['flow']=='COMPUTED_CALL'
at=0x60804+load['length'];between=[]
while at<r['site']:
 i=owner[at];assert i['flow']=='FALL_THROUGH' and not {'RCX','ECX','CX','CL','CH'}&set(i['written_registers']);between.append(at);at+=i['length']
assert at==r['site']
body={i['rva']:i for x in raw if x['start']==r['target'] for i in x['instructions']};assert set(body)=={i['rva'] for i in r['target_body']}
for i in r['target_body']:assert (i['size'],i['bytes'])==(body[i['rva']]['length'],body[i['rva']]['bytes'])
assert [body[x]['text'] for x in sorted(body)]==['XOR EAX,EAX','CMP RDI,RDX','CMOVZ RAX,RSI','RET']
r.update(status='independent RTTI symbol-dispatch candidate passed',proposal_path=str(a.proposal/'proposal.json'),independent_chain=s['chain'],independent_source=[lea,load,call],independent_body=[body[x] for x in sorted(body)],shared_instructions=len(owner)+len(body),return_relation='For this exact body under a normal SysV call: RAX equals incoming RSI if incoming RDI equals incoming RDX; otherwise zero. This does not prove the caller object identity or close the second virtual call.',
 evidence={str(p):sha(p) for p in [a.proposal/'proposal.json',a.proposal/'symbol-input.json',a.symbols/'dispatch.json',a.symbols/'summary.json',a.windows/'summary.json',a.windows/'libc.prx/ghidra.json',Path('tools/ghidra_scripts/BBCheckSymbolDispatch.java')]})
write_json(a.out/'checked.json',r);print(json.dumps(dict(status=r['status'],shared_instructions=r['shared_instructions'],candidate=hex(r['target']),unknown_calls_retained=True)))
