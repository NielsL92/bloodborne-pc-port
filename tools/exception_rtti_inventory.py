"""Investigate one initial RTTI dispatch through symbol-based relocations."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage,PT_SCE_DYNLIBDATA
from tools.startup_service_inventory import LIBC

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 h,path=db.execute("SELECT hash,path FROM module WHERE name='libc.prx'").fetchone();assert h==LIBC and sha(path)==h
 im=ElfImage(Path(path).read_bytes());link=im.linkage();tags=dict(im.dynamic());dyn=next(s for s in im.segments if s.type==PT_SCE_DYNLIBDATA)
 rel={r['offset']:r for r in link['relocations']};decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
 segments=[]
 for n,s in enumerate(im.segments):
  if s.type not in (1,0x61000010) or not s.filesz:continue
  f=a.out/f'segment-{n}.bin';f.write_bytes(im.file_bytes(s.offset,s.filesz));segments.append(dict(address=s.vaddr,path=str(f.resolve())))
 raw_tables={}
 for name,offset_tag,size_tag in [('relocations',0x6100002f,0x61000031),('symbols',0x61000039,0x6100003f),('strings',0x61000035,0x61000037)]:
  f=a.out/(name+'.bin');f.write_bytes(im.file_bytes(dyn.offset+tags[offset_tag],tags[size_tag]));raw_tables[name]=dict(path=str(f.resolve()),sha256=sha(f),source_file_offset=dyn.offset+tags[offset_tag],size=tags[size_tag])
 def resolve(slot,kind):
  r=rel[slot];assert r['type']==1 and r['table']=='rela';s=link['symbols'][r['symbol']]
  assert s['defined'] and s['type']==kind and s['library']==s['module']=='libc'
  candidates=db.execute('SELECT module,rva FROM symbol WHERE defined=1 AND type=? AND nid=? AND library=? AND provider=?',(kind,s['nid'],'libc','libc')).fetchall()
  assert candidates==[(h,s['value'])],candidates
  return dict(slot=slot,raw_word=im.at_va(slot,8).hex(),relocation=r,symbol=s,initial_target=s['value']+r['addend'],binding='Conditional supplied definition; symbol interposition/loader binding and subsequent writes remain unvalidated')
 first=resolve(0xbe2d0,1);assert first['initial_target']==0xba9d0
 second=resolve(first['initial_target']+0x10,2);target=second['initial_target'];assert target==0x48f00
 owner=0x60750;rows=[dict(rva=x,size=n,bytes=b,mnemonic=mn,operands=ops) for x,n,b,mn,ops in db.execute('SELECT i.rva,i.size,i.bytes,i.mnemonic,i.operands FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,owner))]
 ins={i['rva']:i for i in rows};assert ins[0x607fd]['bytes']=='488d0dccda0500' and ins[0x60804]['bytes']=='488b09' and ins[0x60811]['bytes']=='ff5110'
 symbol_size=second['symbol']['size'];body=[dict(rva=i.address,size=i.size,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in decoder.disasm(im.at_va(target,symbol_size),target)]
 assert body and sum(i['size'] for i in body)==symbol_size==10 and body[-1]['mnemonic']=='ret'
 result=dict(status='initial RTTI symbol-dispatch proposal; independent check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),module=h,module_path=path,module_sha256=h,owner=owner,site=0x60811,object_slot=0xbe2d0,table_offset=0x10,target=target,chain=[first,second],source_instructions=rows,target_body=body,target_has_recovered_entry=bool(db.execute('SELECT 1 FROM recovery_entry WHERE module=? AND start=?',(h,target)).fetchone()),raw_tables=raw_tables,
  limitations=['An initial target candidate only. Keep the original unresolved indirect-call record.','Type-1 ELF64 symbol relocations require the recorded supplied definitions; loader interposition and runtime binding remain unvalidated.','The RTTI object, its virtual table cells and initialization cache are mutable. Code bytes must remain immutable for the compilation manifest.','The second virtual call at 0x6081f uses the returned object and remains unresolved. No unconditional normal-return or nonreturn proof is added.','Symbol size and the small decode window are analysis limits, not standalone proof of a complete function. No game CPU execution.'])
 write_json(a.out/'proposal.json',result)
 write_json(a.out/'windows.json',[dict(module=h,start=owner,end=0x608e1),dict(module=h,start=target,end=target+32)])
 write_json(a.out/'symbol-input.json',dict(segments=segments,**{k:v['path'] for k,v in raw_tables.items()},object_slot=0xbe2d0,table_offset=0x10))
 print(json.dumps(dict(status=result['status'],site=hex(result['site']),target=hex(target),new_entry=not result['target_has_recovered_entry'],body_instructions=len(body))))
if __name__=='__main__':main()
