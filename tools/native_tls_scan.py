"""Check recovered main FS self-pointer loads and their static TLS offset words."""
import argparse,collections,json,sqlite3,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));source=Path('local/cfg/startup-recovery-v31-conditional-repeat');c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h,path=c.execute('select hash,path from module where name=?',('eboot.bin',)).fetchone();assert sha(path)==h;im=ElfImage(Path(path).read_bytes());tls=next(r for r in read('local/runtime/loader-plan-v9-runtime-word/tls.json') if r['module']==h);assert tls['memory_size']==1872 and tls['file_size']==0 and tls['alignment']==16
ph=[s for s in im.segments if s.type==7];assert len(ph)==1 and ph[0].memsz==1872 and not ph[0].filesz and ph[0].align==16
relocs={r['offset'] for r in im.linkage()['relocations']};md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True;rows=c.execute("select module,rva,size,bytes,mnemonic,operands from recovery_instruction where operands like '%fs:%'").fetchall();sites=[];unknown=[]
for module,rva,size,code,mnemonic,operands in rows:
 assert module==h and code=='64488b042500000000' and im.at_va(rva,size).hex()==code
 next_ins=next(md.disasm(im.at_va(rva+size,15),rva+size,count=1));row=dict(module=h,source=rva,bytes=code,next_rva=next_ins.address,next_bytes=next_ins.bytes.hex(),next_instruction=next_ins.mnemonic+' '+next_ins.op_str)
 if next_ins.mnemonic=='add' and next_ins.op_str.startswith('rax, qword ptr [rip ') and next_ins.operands[1].type==X86_OP_MEM and next_ins.operands[1].mem.base==X86_REG_RIP:
  at=next_ins.address+next_ins.size+next_ins.operands[1].mem.disp;offset=struct.unpack('<q',im.at_va(at,8))[0];assert at not in relocs and -1872<=offset<0;row.update(offset_slot=at,offset=offset,main_template_offset=1872+offset,offset_word_has_relocation=False);sites.append(row)
 else:unknown.append(row)
assert len(rows)==328
checked=[]
for window in read('local/cfg/ghidra-startup-tls-v1/eboot.bin/ghidra.json'):
 for row in window['instructions']:
  raw=im.at_va(row['rva'],row['length']);assert raw.hex()==row['bytes'];ins=next(md.disasm(raw,row['rva'],count=1));assert ins.size==row['length'];checked.append(row)
by={r['rva']:r for r in checked};assert by[0x207bf94]['text']=='MOV RAX,qword ptr FS:[0x0]';first=next(r for r in sites if r['source']==0x207bf94);assert first['offset']==-1824 and first['offset_slot']==0x53e44a8
refs=read('local/references/tls-v1/references.json')
for ref in refs['records']:assert sha(Path('local/references/tls-v1')/ref['path'])==ref['sha256']
write_json(a.out/'sites.json',sites);write_json(a.out/'unknown-followups.json',unknown);write_json(a.out/'checked-instructions.json',checked)
result=dict(status='main static TLS offset words and independent FS windows checked',source_db_sha256=sha(source/'analysis.sqlite'),module=h,module_path=path,tls=tls,fs_self_loads=len(rows),immediate_offset_uses=len(sites),unknown_followups=len(unknown),distinct_offsets=sorted({r['offset'] for r in sites}),first_use=first,ghidra_sha256=sha('local/cfg/ghidra-startup-tls-v1/eboot.bin/ghidra.json'),checked_instructions=len(checked),references=refs,baseline_hashes={name:sha(name) for name in ['external/shadPS4/src/core/tls.h','external/shadPS4/src/core/linker.cpp','external/shadPS4/src/core/libraries/kernel/threads/tcb.cpp']},files={name:sha(a.out/name) for name in ['sites.json','unknown-followups.json','checked-instructions.json']},game_execution=False,limitations=['Main FS self pointer and initial-exec storage only. DTV, other TCB fields, dynamic modules and TLS symbol/module references are not resolved by this evidence.','Offset words have no relocations but live in mutable source data; this verifies initial contents, not immutability.','All recovered FS loads are inventoried; only immediate recognized offset uses establish these static offsets. Unknown followups remain explicit.'])
write_json(a.out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['references','baseline_hashes','files','tls']}),flush=True)
