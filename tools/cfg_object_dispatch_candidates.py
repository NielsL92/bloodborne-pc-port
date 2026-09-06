"""Bounded initial dispatch candidates from explicit constructor table writes."""
import argparse,json,sqlite3,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG,X86_REG_RIP
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage,PT_SCE_DYNLIBDATA
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h,path=c.execute("select hash,path from module where name='eboot.bin'").fetchone();assert sha(path)==h
im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;link=im.linkage();rel={r['offset']:r for r in link['relocations']};tags=dict(im.dynamic());dyn=next(s for s in im.segments if s.type==PT_SCE_DYNLIBDATA)
# Preserve complete relocation table bytes for independent parsing; no expected addends supplied.
relocation_bytes=im.file_bytes(dyn.offset+tags[0x6100002f],tags[0x61000031]);(a.out/'relocations.bin').write_bytes(relocation_bytes)
entries=[0xf91390,0xf95810,0xfa6410,0x2ba2b10,0x207fa50,0x20819f0];witnesses=[];selection=[]
for entry in entries:
 rows=list(c.execute('select i.rva,i.size,i.bytes from recovery_owner o cross join recovery_instruction i on i.module=o.module and i.rva=o.rva where o.module=? and o.entry=? order by i.rva',(h,entry)));assert rows
 witnesses.append(dict(module=h,entry=entry,instructions=[dict(pc=pc,size=size,bytes=b) for pc,size,b in rows]));selection.append(dict(module=h,start=entry,reason='shared_factory_dispatch_witness'))

def instruction(pc):
 row=c.execute('select size,bytes from recovery_instruction where module=? and rva=?',(h,pc)).fetchone();assert row
 i=next(decoder.disasm(bytes.fromhex(row[1]),pc,count=1));assert i.size==row[0];return i
specs=[dict(name='constructed-singleton-slot-20',assignment_entry=0x20819f0,lea=0x2081a11,adjust=None,store=0x2081a18,call_entry=0xf91390,call=0xf913e4,offset=0x20,object_offset=0),dict(name='factory-lock-slot-18',assignment_entry=0x207fa50,lea=0x207fab1,adjust=0x207fab8,store=0x207fabc,call_entry=0x207fa50,call=0x207fb12,offset=0x18,object_offset=0),dict(name='factory-lock-slot-28',assignment_entry=0x207fa50,lea=0x207fab1,adjust=0x207fab8,store=0x207fabc,call_entry=0x207fa50,call=0x207fb84,offset=0x28,object_offset=0)]
proposals=[]
for spec in specs:
 lea=instruction(spec['lea']);store=instruction(spec['store']);call=instruction(spec['call']);assert lea.mnemonic=='lea' and lea.operands[1].type==X86_OP_MEM and lea.operands[1].mem.base==X86_REG_RIP
 table=lea.address+lea.size+lea.operands[1].mem.disp
 if spec['adjust']:
  add=instruction(spec['adjust']);assert add.mnemonic=='add' and add.operands[0].reg==lea.operands[0].reg and add.operands[1].type==X86_OP_IMM;table+=add.operands[1].imm
 assert store.mnemonic=='mov' and store.operands[0].type==X86_OP_MEM and store.operands[1].reg==lea.operands[0].reg
 assert call.mnemonic=='call' and call.operands[0].type==X86_OP_MEM and call.operands[0].mem.disp==spec['offset'] and not call.operands[0].mem.index
 slot=table+spec['offset'];r=rel[slot];assert r['type']==8 and r['symbol']==0 and r['table']=='rela'
 assert any(s.flags&1 and s.vaddr<=r['addend']<s.vaddr+s.filesz for s in im.segments if s.type in (1,0x61000010))
 proposals.append(dict(**spec,module=h,table=table,slot=slot,slot_bytes=im.at_va(slot,8).hex(),relocation=r,target=r['addend'],target_has_recovered_body=bool(c.execute('select 1 from recovery_entry where module=? and start=?',(h,r['addend'])).fetchone()),assignment_text=store.mnemonic+' '+store.op_str,call_text=call.mnemonic+' '+call.op_str,conditional='Only the object constructed with this initial table, under the observed factory/cache path. Object identity, initialization races/failure, intervening writes and runtime targets remain unknown.'))
for table in sorted({r['table'] for r in proposals}):(a.out/(hex(table)+'.bin')).write_bytes(im.at_va(table,0x30))
profile=dict(status='initial object dispatch proposals; independent source/table check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),module=h,module_path=path,proposals=proposals,witnesses=witnesses,relocation_table_sha256=sha(a.out/'relocations.bin'),relocation_table_file_offset=dyn.offset+tags[0x6100002f],is_self=im.is_self,source_conditions=['Shared thunk 0x2ba2b10 jumps to factory 0x207fa50.','Null constructor cache 0x5540670 invokes the factory; a non-null cache remains a mutable unknown object.','Factory has mutable singleton slot 0x56a20c0 and conditionally constructs aligned storage at 0x56a20c8 via 0x20819f0.','Factory lock object has an explicit table write before its virtual calls on its initialization path; other paths depend on mutable initialized state.','Only the three specified slots are inspected. Adjacent pointers or zero words are not promoted or taken as table extent.'],limitations='Static candidate compilation work only. No indirect site is closed, no game CPU execution, and no assertion of unique runtime object type or table immutability.')
write_json(a.out/'proposals.json',profile);write_json(a.out/'selection.json',selection);write_json(a.out/'table-input.json',dict(relocations=str((a.out/'relocations.bin').resolve()),tables=[dict(address=table,path=str((a.out/(hex(table)+'.bin')).resolve())) for table in sorted({r['table'] for r in proposals})],slots=[dict(name=r['name'],slot=r['slot']) for r in proposals]))
print(json.dumps(dict(status=profile['status'],targets=[hex(r['target']) for r in proposals],already_recovered=[r['target_has_recovered_body'] for r in proposals],witnesses=len(witnesses))),flush=True)
