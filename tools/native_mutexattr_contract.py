"""Bind only exact mutex-attribute identities supported by supplied caller evidence."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));registry=Path('local/runtime/registry-v7-memory-repeat');imports=read(registry/'imports.json');source=Path('local/cfg/startup-recovery-v31-conditional-repeat');db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h,path=db.execute('select hash,path from module where name=?',('eboot.bin',)).fetchone();assert sha(path)==h;im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);checked=[]
for window in read('local/cfg/ghidra-startup-mutex-v2-full/eboot.bin/ghidra.json'):
 for row in window['instructions']:
  raw=im.at_va(row['rva'],row['length']);assert raw.hex()==row['bytes'];ins=next(decoder.disasm(raw,row['rva'],count=1));assert ins.size==row['length'];checked.append(dict(**row,capstone=ins.mnemonic+' '+ins.op_str))
by={r['rva']:r for r in checked}
for at,code in [(0x2083ffe,'4c8d75d8'),(0x2084002,'4c89f7'),(0x208400a,'be02000000'),(0x208400f,'4c89f7'),(0x208401c,'4c89f6'),(0x2084026,'4c89f7'),(0x2084037,'81fb0c000280'),(0x208403f,'81fb16000280')]:assert by[at]['bytes']==code
for at,target in [(0x2084005,0x2bbfea8),(0x2084012,0x2bbfeb8),(0x208401f,0x2bbfec8),(0x2084029,0x2bbfed8)]:assert by[at]['targets']==[target]
services={'F8bUHwAG284':'mutexattr_init','iMp8QpE+XO4':'mutexattr_settype','smWEktiyyG0':'mutexattr_destroy'};bindings=[]
for nid,handler in services.items():
 canonical=next(r for r in imports if r.get('canonical') and r['nid']==nid and r['library']==r['module']=='libkernel');assert canonical['library_version']==1 and canonical['module_version']==257 and not canonical['compiled_export']
 for imp in imports:
  if imp['pc']==canonical['pc'] or imp.get('canonical_service_pc')==canonical['pc']:
   assert imp['nid']==nid and imp['library']==imp['module']=='libkernel' and not imp['compiled_export'];bindings.append(dict(pc=imp['pc'],canonical_pc=canonical['pc'],handler=handler,nid=nid,library='libkernel',library_version=1,module='libkernel',module_version=257))
assert {r['pc'] for r in bindings}>={0x102bbfea8,0x102bbfeb8,0x102bbfed8};bindings.sort(key=lambda r:r['pc']);assert len(bindings)==len({r['pc'] for r in bindings})
reference=read('local/references/mutexattr-v1/reference.json');assert sha('local/references/mutexattr-v1/thr_mutexattr.c')==reference['sha256'];authored=read('local/runtime/mutexattr-v1/summary.json');assert authored['positive']['aot_service_calls']==45059
contract=dict(status='bounded mutex-attribute service interface checked',registry_identity=sha(registry/'identity.json'),bindings=bindings,logical_identifier_range=[0x71000000000,0x71100000000],live_limit=4096,argument_storage_bytes=8,default_policy=dict(type=1,protocol=0,ceiling=0,provenance='Explicit native defaults matching the pinned baseline; the reached caller overwrites type with 2 before mutex creation.'),return_abi='32-bit EAX; success zero, native invalid-handle/type 0x80020016, resource exhaustion 0x8002000c; preserve SysV callee-saved registers and return through the logical stack',primary_reference=reference,checked_instructions=len(checked),ghidra_sha256=sha('local/cfg/ghidra-startup-mutex-v2-full/eboot.bin/ghidra.json'),authored_sha256=sha('local/runtime/mutexattr-v1/summary.json'),limitations=['The supplied caller proves pointer-sized attribute storage and by-reference init/settype/destroy use; it does not prove a full guest-readable private object layout.','Native opaque identifiers never expose host pointers. Guest dereference of these identifiers stops until an independently checked object-layout interface is added.','Defaults, null/invalid diagnostics and resource bounds are explicit native compatibility policies. These references are not console observations.','Mutex creation, locking, protocol/ceiling/process-sharing setters and POSIX-namespace aliases are not supplied by these three bindings.'],game_aot_execution=False)
write_json(a.out/'checked-instructions.json',checked);write_json(a.out/'contract.json',contract);print(json.dumps(dict(status=contract['status'],bindings=len(bindings),instructions=len(checked))),flush=True)
