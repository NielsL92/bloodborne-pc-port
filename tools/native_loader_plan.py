"""Plan private module data loading without executing code or inventing symbol values."""
import argparse,collections,json,struct
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('registry',type=Path);p.add_argument('constructors',type=Path);p.add_argument('out',type=Path);p.add_argument('--weak-bindings',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
modules=read(a.registry/'modules.json');registered=read(a.registry/'imports.json');canonical={}
for item in registered:
 if item.get('canonical'):
  for use in item['uses']:
   key=use['module'],use['symbol_index'];assert key not in canonical;canonical[key]=item
exports=collections.defaultdict(list);images={};links={};regions=[];tls=[];module_rows=[]
for index,module in enumerate(modules):
 h=module['module'];path=Path(module['path']);assert sha(path)==h;im=images[h]=ElfImage(path.read_bytes());link=links[h]=im.linkage();base=module['logical_base'];segments=[]
 for n,ph in enumerate(im.segments):
  if ph.type in [1,0x61000010] and ph.memsz:
   assert ph.vaddr+ph.memsz<0x100000000 and ph.flags&~7==0;assert not (ph.flags&1 and ph.flags&2),'writable source code segment'
   size=(ph.memsz+max(ph.align,4096)-1)&-max(ph.align,4096);start=base+ph.vaddr;assert not any(start<r['base']+r['mapped_size'] and r['base']<start+size for r in regions),'overlapping rounded logical mappings'
   data=im.file_bytes(ph.offset,ph.filesz);file=f'module-{index:02d}-segment-{n:02d}.bin';(a.out/file).write_bytes(data)
   row=dict(module=h,header_index=n,base=start,elf_rva=ph.vaddr,mapped_size=size,declared_memory_size=ph.memsz,file_size=ph.filesz,zero_tail=size-ph.filesz,elf_flags=ph.flags,native_rights=(1 if ph.flags&4 else 0)|(2 if ph.flags&2 else 0)|(4 if ph.flags&1 else 0),initial_file=file,initial_sha256=sha(a.out/file),guest_executable=False);regions.append(row);segments.append(row)
  if ph.type==7:
   assert ph.filesz<=ph.memsz;tls.append(dict(module=h,module_id=index+1,template_pc=base+ph.vaddr,file_size=ph.filesz,memory_size=ph.memsz,alignment=ph.align,initial_hex=im.file_bytes(ph.offset,ph.filesz).hex(),note='Logical module IDs follow this explicit registry order; per-thread layout is not selected.'))
 for symbol in link['symbols']:
  if symbol['defined'] and symbol['name']:exports[tuple(symbol[k] for k in ['nid','library','module','type'])].append(dict(owner=h,pc=base+symbol['value'],symbol=symbol))
 tags=dict(im.dynamic());module_rows.append(dict(**module,elf_type=im.type,entry_rva=im.entry,entry_pc=base+im.entry,dynamic_initializers={hex(t):v for t,v in im.dynamic() if t in [12,13,25,26,27,28,32,33]},needed=link['needed'],import_libraries=link['libraries'],import_modules=link['modules'],export_libraries=link['export_libraries'],export_modules=link['export_modules'],segments=len(segments)))
weak={}
if a.weak_bindings:
 weak_summary=read(a.weak_bindings/'summary.json');assert weak_summary['ghidra_checked'];assert weak_summary['bindings_sha256']==sha(a.weak_bindings/'weak-bindings.json');weak={(r['module'],r['relocation']['offset']):r for r in read(a.weak_bindings/'weak-bindings.json')}
counts=collections.Counter();unresolved=[];planned={};relocations=[];code_writes=[];version_disputes=[]
for index,module in enumerate(modules):
 h=module['module'];base=module['logical_base'];link=links[h]
 for row in link['relocations']:
  at=base+row['offset'];owners=[r for r in regions if r['base']<=at and at+8<=r['base']+r['declared_memory_size']];assert len(owners)==1,('relocation outside declared segment',module['name'],row);owner=owners[0];assert (h,row['offset']) not in planned,'duplicate relocation destination';symbol=link['symbols'][row['symbol']];value=None;kind='unresolved';detail=None
  if (h,row['offset']) in weak:
   checked=weak[h,row['offset']];assert checked['relocation']==row and checked['symbol']==symbol;value=0;kind='checked absent weak callback'
  elif row['type']==8:value=(base+row['addend'])&0xffffffffffffffff;kind='relative'
  elif row['type']==16:
   if row['symbol']==0:value=index+1;kind='local TLS module identifier'
   else:detail='DTPMOD64 references a symbol; module resolution requires independent validation'
  elif row['type'] in [1,6,7]:
   addend=row['addend'] if row['type']==1 else 0
   if row['type'] in [6,7] and row['addend']!=0:detail='nonzero GLOB_DAT/JUMP_SLOT addend requires review'
   elif symbol['defined'] and symbol['bind']==0:value=(base+symbol['value']+addend)&0xffffffffffffffff;kind='local defined symbol'
   else:
    candidates=exports.get(tuple(symbol[k] for k in ['nid','library','module','type']),[])
    if len(candidates)==1:
     selected=candidates[0];target_link=links[selected['owner']];required=[r for r in link['libraries'] if r['name']==symbol['library']];provided=[r for r in target_link['export_libraries'] if r['name']==symbol['library']]
     versions_match=len(required)==len(provided)==1 and required[0]['version']==provided[0]['version']
     required_modules=[r for r in link['modules'] if r['name']==symbol['module']];provided_modules=[r for r in target_link['export_modules'] if r['name']==symbol['module']]
     versions_match=versions_match and len(required_modules)==len(provided_modules)==1 and required_modules[0]['version']==provided_modules[0]['version']
     if symbol['defined'] and selected['owner']==h:versions_match=True
     if versions_match:value=(selected['pc']+addend)&0xffffffffffffffff;kind='conditional static symbol binding'
     else:detail='library/module version identity is not established';version_disputes.append(dict(module=h,symbol=symbol,candidate=selected,required=required,provided=provided,required_modules=required_modules,provided_modules=provided_modules))
    elif symbol['type']==2 and (h,symbol['index']) in canonical:
     service=canonical[h,symbol['index']];assert all(service[k]==symbol[k] for k in ['nid','library','module']);value=(service['pc']+addend)&0xffffffffffffffff;kind='canonical native service identity'
    elif symbol['type']==2:
     options=[r for r in registered if r['source_module']==h and all(r[k]==symbol[k] for k in ['nid','library','module'])]
     if len(options)==1 and not options[0]['compiled_export']:value=(options[0]['pc']+addend)&0xffffffffffffffff;kind='registered native service gateway'
     else:detail='function has no unique registered binding in the current startup closure'
    else:detail='data/undefined symbol has no unique supplied binding'
  else:detail='unhandled relocation kind'
  record=dict(module=h,offset=row['offset'],type=row['type'],symbol_index=row['symbol'],addend=row['addend'],value=value,kind=kind)
  if owner['elf_flags']&1:code_writes.append(record)
  if value is None:record.update(detail=detail,symbol=symbol);unresolved.append(record)
  counts[kind]+=1;planned[h,row['offset']]=record;relocations.append(record)
write_json(a.out/'modules.json',module_rows);write_json(a.out/'regions.json',regions);write_json(a.out/'tls.json',tls);write_json(a.out/'unresolved-relocations.json',unresolved);write_json(a.out/'version-disputes.json',version_disputes);write_json(a.out/'code-relocations.json',code_writes)
with (a.out/'relocations.jsonl').open('w',encoding='utf-8') as f:
 for row in relocations:f.write(json.dumps(row,separators=(',',':'))+chr(10))
main=next(m for m in modules if m['name']=='eboot.bin');constructors=read(a.constructors);ordered=[]
for row in constructors:
 reloc=planned[main['module'],row['slot']];assert reloc['kind']=='relative' and reloc['value']==main['logical_base']+row['target'];ordered.append(dict(ordinal=row['ordinal'],slot=main['logical_base']+row['slot'],target=reloc['value'],writable_table=next(r for r in regions if r['base']<=main['logical_base']+row['slot']<r['base']+r['declared_memory_size'])['native_rights']&2!=0))
assert len(ordered)==18444 and [r['ordinal'] for r in ordered]==list(range(18444));write_json(a.out/'constructor-order.json',ordered)
summary=dict(status='native loader plan inventoried; unresolved relocations prohibit execution',registry_identity_sha256=sha(a.registry/'identity.json'),weak_bindings_sha256=sha(a.weak_bindings/'weak-bindings.json') if a.weak_bindings else None,modules=len(modules),regions=len(regions),mapped_bytes=sum(r['mapped_size'] for r in regions),initial_bytes=sum(r['file_size'] for r in regions),zero_bytes=sum(r['zero_tail'] for r in regions),relocations=len(relocations),classification=dict(counts),unresolved_relocations=len(unresolved),code_relocations=len(code_writes),version_disputes=len(version_disputes),constructor_targets_checked=len(ordered),tls_records=len(tls),tls_nonempty=sum(bool(r['memory_size']) for r in tls),game_execution=False,native_loading_performed=False,files={p.name:sha(p) for p in sorted(a.out.iterdir()) if p.is_file()},limitations=['Copied segment bytes only. No original/hardlinked file modifications.','No unresolved relocation is assigned zero or a guessed address.','Static symbol bindings remain conditional on the declared module/version and interposition model.','Constructor order is evidence for actual compiled startup, not permission to call the initial table entries manually.','Private host mappings, per-thread TLS, startup ABI and actual entry execution remain unimplemented.'])
write_json(a.out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['files','limitations']}),flush=True)
