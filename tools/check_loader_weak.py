"""Check absent weak module callbacks and their bounded PLT instruction identities."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
from tools.formats import ElfImage
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('registry',type=Path);p.add_argument('out',type=Path);p.add_argument('--ghidra',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
modules=read(a.registry/'modules.json');assert all(sha(Path(r['path']))==r['module'] for r in modules);images={r['module']:ElfImage(Path(r['path']).read_bytes()) for r in modules};links={h:i.linkage() for h,i in images.items()};definitions={s['name'] for link in links.values() for s in link['symbols'] if s['defined']};md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True;rows=[];windows=[]
for module in modules:
 h=module['module'];im=images[h];link=links[h]
 for rel in link['relocations']:
  symbol=link['symbols'][rel['symbol']]
  if symbol['bind']!=2 or symbol['defined'] or symbol['name'] not in ['module_start','module_stop']:continue
  assert rel['type']==7 and rel['addend']==0 and symbol['type']==0 and symbol['value']==symbol['size']==0 and symbol['library'] is None and symbol['module'] is None and symbol['name'] not in definitions
  stub=struct.unpack('<Q',im.at_va(rel['offset'],8))[0]-6;raw=im.at_va(stub,6);ins=next(md.disasm(raw,stub,count=1));assert ins.mnemonic=='jmp' and ins.size==6 and len(ins.operands)==1 and ins.operands[0].type==X86_OP_MEM and ins.operands[0].mem.base==X86_REG_RIP and stub+6+ins.operands[0].mem.disp==rel['offset']
  rows.append(dict(module=h,name=module['name'],symbol=symbol,relocation=rel,stub_rva=stub,stub_bytes=raw.hex(),value=0,evidence='Undefined weak module callback, absent across this fixed module set; ELF weak-zero contract.'))
  windows.append(dict(module=h,start=stub,end=stub+6))
assert len(rows)==12
if a.ghidra:
 observed={}
 for module in read(a.ghidra/'summary.json')['modules']:
  for window in read(a.ghidra/module['name']/'ghidra.json'):
   assert len(window['instructions'])==1;ins=window['instructions'][0];observed[module['module'],ins['rva']]=ins
 for row in rows:
  ins=observed[row['module'],row['stub_rva']];assert ins['bytes']==row['stub_bytes'] and ins['length']==6 and ins['flow']=='COMPUTED_JUMP';row['ghidra_text']=ins['text']
write_json(a.out/'weak-bindings.json',rows);write_json(a.out/'ghidra-windows.json',windows)
summary=dict(status='twelve weak-zero callback bindings checked',bindings=len(rows),ghidra_checked=bool(a.ghidra),registry_identity_sha256=sha(a.registry/'identity.json'),bindings_sha256=sha(a.out/'weak-bindings.json'),source='https://gabi.xinuos.com/elf/05-symtab.html',scope='Fixed supplied module set only. This rule does not zero strong imports, provide a native service success result, or establish callback execution.',game_execution=False)
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
