"""Extend checked attribute services with bounded native mutex ownership interfaces."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));old=Path('local/runtime/mutexattr-contract-v1');contract=read(old/'contract.json');imports=read('local/runtime/registry-v7-memory-repeat/imports.json');source=Path('local/cfg/startup-recovery-v31-conditional-repeat');db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h,path=db.execute('select hash,path from module where name=?',('eboot.bin',)).fetchone();assert sha(path)==h;im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);checked=[]
for window in read('local/cfg/ghidra-startup-mutex-v3-ownership/eboot.bin/ghidra.json'):
 for row in window['instructions']:
  raw=im.at_va(row['rva'],row['length']);assert raw.hex()==row['bytes'];ins=next(decoder.disasm(raw,row['rva'],count=1));assert ins.size==row['length'];checked.append(dict(**row,capstone=ins.mnemonic+' '+ins.op_str))
by={r['rva']:r for r in checked}
for at,target in [(0x208401f,0x2bbfec8),(0x207eec4,0x2bbfef8),(0x207f0a4,0x2bbff08),(0x20840b4,0x2bbfee8)]:assert by[at]['targets']==[target]
services={'cmo1RIYva9o':'mutex_init','9UK1vLZQft4':'mutex_lock','tn3VlD0hG60':'mutex_unlock','2Of0f+3mhhE':'mutex_destroy'};bindings=contract['bindings'][:]
for nid,handler in services.items():
 canonical=next(r for r in imports if r.get('canonical') and r['nid']==nid and r['library']==r['module']=='libkernel');assert canonical['library_version']==1 and canonical['module_version']==257 and not canonical['compiled_export']
 for imp in imports:
  if imp['pc']==canonical['pc'] or imp.get('canonical_service_pc')==canonical['pc']:
   assert imp['nid']==nid and imp['library']==imp['module']=='libkernel' and not imp['compiled_export'];bindings.append(dict(pc=imp['pc'],canonical_pc=canonical['pc'],handler=handler,nid=nid,library='libkernel',library_version=1,module='libkernel',module_version=257))
bindings.sort(key=lambda r:r['pc']);assert len(bindings)==len({r['pc'] for r in bindings});one=read('local/runtime/mutex-v1/summary.json');two=read('local/runtime/mutex-v2-repeat/summary.json');assert one==two and two['positive']['aot_service_calls']==53267
ref=read('local/references/mutex-v1/reference.json');assert sha('local/references/mutex-v1/thr_mutex.c')==ref['sha256']
contract.update(status='bounded native mutex ownership interfaces checked',parent_contract_sha256=sha(old/'contract.json'),bindings=bindings,mutex_services=True,mutex_live_limit=65536,mutex_identifier_range=[0x72000000000,0x72100000000],checked_instructions=len(checked),ghidra_sha256=sha('local/cfg/ghidra-startup-mutex-v3-ownership/eboot.bin/ghidra.json'),mutex_authored_sha256=sha('local/runtime/mutex-v2-repeat/summary.json'),mutex_reference=ref,windows_reference='https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleepconditionvariablecs')
contract['limitations']+=['Uncontended/contended mutex ownership and recursive depth use native critical sections and condition variables. This does not implement guest thread creation or scheduling.','Named, static-initializer, nondefault-protocol, timed, robust and guest-readable private mutex layouts remain explicit unsupported interfaces. Normal-mutex self-deadlock stops diagnostically instead of hanging forever.','Four SCE ownership identities are bound; trylock is authored-tested but remains unbound pending a reached caller contract.','All native resource/default policies and the earlier attribute-layout uncertainty remain explicit.']
write_json(a.out/'checked-instructions.json',checked);write_json(a.out/'contract.json',contract);print(json.dumps(dict(status=contract['status'],bindings=len(bindings),instructions=len(checked))),flush=True)
