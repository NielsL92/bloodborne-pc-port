"""Inventory exact canary imports and independently checkable supplied read prefixes."""
import argparse,collections,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_MEM,X86_OP_REG,X86_REG_RIP
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
plan=Path('local/runtime/loader-plan-v8-memory');source=Path('local/cfg/startup-recovery-v31-conditional-repeat');modules=read(plan/'modules.json');unresolved=read(plan/'unresolved-relocations.json');uses=[];slots={};names={};images={}
for module in modules:
 h=module['module'];names[h]=module['name'];assert sha(module['path'])==h;im=images[h]=ElfImage(Path(module['path']).read_bytes());link=im.linkage();rows=[r for r in unresolved if r['module']==h and r['symbol']['nid']=='f7uOxY9mM1U'];assert len(rows)==1;r=rows[0];symbol=r['symbol'];assert symbol['type']==1 and symbol['bind']==1 and not symbol['defined'] and symbol['size']==0 and r['type']==6 and r['addend']==0
 libraries=[v for v in link['libraries'] if v['name']==symbol['library']];owners=[v for v in link['modules'] if v['name']==symbol['module']];assert len(libraries)==len(owners)==1;assert symbol['library']==symbol['module']=='libkernel' and libraries[0]['version']==1 and owners[0]['version']==257
 uses.append(dict(module=h,name=module['name'],base=module['logical_base'],relocation=r,library_version=1,module_version=257));slots[h,r['offset']]=r
c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;refs=[];selected={}
for h,rva,size,code in c.execute("select module,rva,size,bytes from recovery_instruction where operands like '%rip%' order by module,rva"):
 ins=next(decoder.disasm(bytes.fromhex(code),rva,count=1));assert ins.size==size
 for index,op in enumerate(ins.operands):
  if op.type!=X86_OP_MEM or op.mem.base!=X86_REG_RIP:continue
  slot=rva+size+op.mem.disp
  if (h,slot) not in slots:continue
  record=dict(module=h,rva=rva,bytes=code,text=ins.mnemonic+' '+ins.op_str,slot=slot,width=op.size,access=op.access,kind='unclassified slot reference');refs.append(record)
  if ins.mnemonic!='mov' or len(ins.operands)!=2 or index!=1 or ins.operands[0].type!=X86_OP_REG or ins.operands[0].size!=8 or op.size!=8:continue
  record['kind']='64-bit GOT pointer load';register=ins.operands[0].reg
  if h in selected:continue
  at=rva+size;prefix=[dict(rva=rva,bytes=code,text=record['text'])]
  for step in range(16):
   row=c.execute('select bytes,size from recovery_instruction where module=? and rva=?',(h,at)).fetchone()
   if row is None:break
   raw=bytes.fromhex(row[0]);next_ins=next(decoder.disasm(raw,at,count=1));assert next_ins.size==row[1];prefix.append(dict(rva=at,bytes=raw.hex(),text=next_ins.mnemonic+' '+next_ins.op_str))
   operands=[v for v in next_ins.operands if v.type==X86_OP_MEM and v.mem.base==register and not v.mem.index and v.mem.disp==0]
   if operands:
    if len(operands)==1 and operands[0].size==8 and operands[0].access==1:selected[h]=dict(module=h,start=rva,end=at+next_ins.size,slot=slot,read_rva=at,read_size=8,prefix=prefix)
    break
   if next_ins.group(CS_GRP_CALL) or next_ins.group(CS_GRP_JUMP) or next_ins.group(CS_GRP_RET) or register in next_ins.regs_access()[1]:break
   at+=next_ins.size
assert len(uses)==8
write_json(a.out/'uses.json',uses);write_json(a.out/'slot-references.json',refs);write_json(a.out/'selected-prefixes.json',[selected[h] for h in sorted(selected)]);write_json(a.out/'windows.json',[{k:r[k] for k in ['module','start','end']} for h,r in sorted(selected.items())]);summary=dict(status='canary object import/read candidates inventoried',uses=len(uses),slot_references=len(refs),classes=dict(collections.Counter(r['kind'] for r in refs)),reference_widths=dict(collections.Counter(r['width'] for r in refs)),selected_read_prefixes=len(selected),missing_recovered_prefixes=[names[h] for h in names if h not in selected],source_db_sha256=sha(source/'analysis.sqlite'),registry_identity=sha(Path('local/runtime/registry-v7-memory-repeat/identity.json')),limits=['Symbol size is absent; eight-byte pointee width is evidence from supplied loads, not unwind or symbol-size inference.','Static references/prefixes do not prove absence of indirect writes, dynamic interposition, pointer escape or wider accesses.','No data binding, random initialization or guard removal is performed.']);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
