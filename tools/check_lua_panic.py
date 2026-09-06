"""Check SLEIGH field operands and public header evidence before exporting candidates."""
import argparse,json,re
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.cfg_lua_panic import validate_candidate
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('owners',type=Path);p.add_argument('closure',type=Path);p.add_argument('targets',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
r=read(a.proposal/'proposal.json');closure=read(a.closure/'checked.json');target_summary=read(a.targets/'summary.json')
assert closure['status']=='independent window closure comparison passed' and closure['unexplained']==0
assert closure['source_db_sha256']==r['source_db_sha256']==target_summary['source_db_sha256']
assert closure['selection_sha256']==sha(a.proposal/'selection.json') and closure['comparison_sha256']==sha(a.owners/'comparison.json')
assert closure['raw_sha256']['eboot.bin']==sha(a.owners/'eboot.bin/ghidra.json')
assert target_summary['requests_sha256']==sha(a.proposal/'windows.json')
assert target_summary['modules'][0]['raw_sha256']==sha(a.targets/'eboot.bin/ghidra.json')
owners={w['start']:{i['rva']:i for i in w['instructions']} for w in read(a.owners/'eboot.bin/ghidra.json')};targets={w['start']:{i['rva']:i for i in w['instructions']} for w in read(a.targets/'eboot.bin/ghidra.json')}
for o in r['owners']:
 for i in o['instructions']:assert (i['size'],i['bytes'])==(owners[o['entry']][i['rva']]['length'],owners[o['entry']][i['rva']]['bytes'])
def text(entry,pc,expected):assert owners[entry][pc]['text']==expected,(hex(pc),owners[entry][pc]['text'])
text(r['owner'],r['global_load'],'MOV RAX,qword ptr [RDI + 0x20]');text(r['owner'],r['site'],'CALL qword ptr [RAX + 0x50]')
assert owners[r['owner']][r['site']]['flow']=='COMPUTED_CALL'
for x in r['assignments']:
 text(x['entry'],x['lea'],f"LEA RCX,[0x{x['target']:x}]");text(x['entry'],x['store'],'MOV qword ptr [RAX + 0x50],RCX')
 actual=targets[x['target']];assert set(actual)=={i['rva'] for i in x['body']}
 for i in x['body']:assert (i['size'],i['bytes'])==(actual[i['rva']]['length'],actual[i['rva']]['bytes'])
 assert actual[x['body'][-1]['rva']]['flow']=='TERMINATOR'
# Distinguish the real allocator extension and state/global fields. These remain
# source-family and conditional object-role witnesses, not a complete alias proof.
roles=[(0x2114d70,0x2114d85,'MOV EDX,0xc0'),(0x2114d70,0x2114e30,'MOV qword ptr [RBX + 0xa8],R14'),(0x2114d70,0x2114e90,'LEA RSI,[0x2115080]'),(0x2114d70,0x2114e9c,'CALL 0x0210adb0'),(0x2115080,0x211508e,'MOV RDI,qword ptr [R14 + 0xa8]'),(0x2115080,0x211509a,'MOV EDX,0x120'),(0x2115080,0x21150ab,'MOV qword ptr [R14 + 0x20],RAX'),(0x20fbc50,0x20fbcab,'CALL 0x02114d70'),(0x20fbc50,0x20fbcc4,'MOV RAX,qword ptr [RAX + 0x20]'),(0x210adb0,0x210adc5,'MOV R14,RSI'),(0x210adb0,0x210ae13,'CALL R14')]
for args in roles:text(*args)
assert sha(r['module_path'])==r['module'];im=ElfImage(Path(r['module_path']).read_bytes())
validate_candidate(r,{r['module']:im},lambda h,pc:any(s.type in (1,0x61000010) and s.flags&1 and s.vaddr<=pc<s.vaddr+s.filesz for s in im.segments))
for f,digest in r['evidence'].items():assert sha(f)==digest
r.update(status='independent Lua panic field candidates passed',proposal_path=str(a.proposal/'proposal.json'),shared_instructions=closure['shared_instructions']+sum(len(t) for t in targets.values()),independent_roles=[dict(entry=e,rva=pc,text=t) for e,pc,t in roles])
for f in [a.proposal/'proposal.json',a.proposal/'selection.json',a.proposal/'windows.json',a.owners/'eboot.bin/ghidra.json',a.owners/'comparison.json',a.closure/'checked.json',a.targets/'summary.json',a.targets/'eboot.bin/ghidra.json']:r['evidence'][str(f)]=sha(f)
write_json(a.out/'checked.json',r);print(json.dumps(dict(status=r['status'],shared=r['shared_instructions'],targets=[hex(x['target']) for x in r['assignments']],unknown_call_retained=True)))
