"""Inventory exact mutable Lua panic stores; preserve alias and source-version uncertainty."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
from tools.startup_service_inventory import MAIN
OWNERS=(0x210ad70,0x210adb0,0x2114d70,0x2115080,0x20fbc50)
ASSIGNMENTS=((0x2115080,0x21150f7,0x21150fe,0x21155e0,3,'default global initialization'),(0x20fbc50,0x20fbcc8,0x20fbccf,0x2100e00,23,'game wrapper override'))
def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('reference',type=Path);p.add_argument('layout',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 h,path=db.execute("SELECT hash,path FROM module WHERE name='eboot.bin'").fetchone();assert h==MAIN and sha(path)==h
 im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);owners=[]
 for entry in OWNERS:
  rows=[dict(rva=x,size=n,bytes=b,mnemonic=mn,operands=ops) for x,n,b,mn,ops in db.execute('SELECT i.rva,i.size,i.bytes,i.mnemonic,i.operands FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,entry))]
  assert rows and rows[0]['rva']==entry;owners.append(dict(entry=entry,instructions=rows))
 assignments=[]
 for entry,lea,store,target,size,role in ASSIGNMENTS:
  body=[dict(rva=i.address,size=i.size,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in decoder.disasm(im.at_va(target,size),target)]
  assert sum(i['size'] for i in body)==size and body[-1]['mnemonic']=='ret'
  assignments.append(dict(entry=entry,lea=lea,store=store,target=target,analysis_size=size,role=role,body=body,already_recovered=bool(db.execute('SELECT 1 FROM recovery_entry WHERE module=? AND start=?',(h,target)).fetchone())))
 identity=json.loads((a.reference/'identity.json').read_text(encoding='utf-8'));layout=json.loads((a.layout/'summary.json').read_text(encoding='utf-8'))
 assert layout['reference_identity_sha256']==sha(a.reference/'identity.json')
 for f,digest in identity['files'].items():assert sha(a.reference/f)==digest
 marker=im.data.find(b'Lua 5.0.2') if hasattr(im,'data') else Path(path).read_bytes().find(b'Lua 5.0.2')
 assert marker>=0
 r=dict(status='Lua panic field candidates proposed; independent check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),module=h,module_sha256=h,module_path=path,owner=0x210ad70,site=0x210ad84,global_load=0x210ad80,global_offset=0x20,field_offset=0x50,owners=owners,assignments=assignments,public_reference_identity_sha256=sha(a.reference/'identity.json'),header_layout_sha256=sha(a.layout/'summary.json'),version_marker_file_offset=marker,observed_state_allocation_bytes=192,public_lp64_state_bytes=160,extra_allocator_offset=0xa8,
  evidence={str(p):sha(p) for p in [a.reference/'identity.json',a.reference/'lua-5.0.2/src/ldo.c',a.reference/'lua-5.0.2/src/lstate.c',a.reference/'lua-5.0.2/src/lstate.h',a.layout/'summary.json',a.layout/'layout.c',a.layout/'x86_64-unknown-freebsd.ll',a.layout/'x86_64-pc-windows-msvc.ll']},
  conditions=['The throw helper receives a valid customized Lua state with the observed LP64-compatible prefix.','The initializer or wrapper store applies to the same global object used by this call, with normal SysV returns and preserved registers.','A candidate remains applicable only until a subsequent callback-field write; this is not a complete mutation or setter inventory.'],
  limitations=['Keep the original unknown indirect call and ordinary call fallthrough. These candidates do not establish a no-return contract.','The public version marker and matching offsets identify a source family, not an unmodified library: the supplied state is 192 bytes with extensions at and beyond 0xa0.','Other offset-0x50 stores can be Lua base_ci or wrapper fields, not the panic callback.','No host jmp_buf layout, native runtime binding, exception transfer, constructor immutability or execution coverage is inferred.'])
 write_json(a.out/'proposal.json',r);write_json(a.out/'selection.json',[dict(module=h,start=x,reason='Lua panic field and customized state provenance') for x in OWNERS]);write_json(a.out/'windows.json',[dict(module=h,start=x['target'],end=x['target']+x['analysis_size']+32) for x in assignments])
 print(json.dumps(dict(status=r['status'],owners=len(owners),new_targets=[hex(x['target']) for x in assignments if not x['already_recovered']],state_bytes=192,public_state_bytes=160)))
if __name__=='__main__':main()
