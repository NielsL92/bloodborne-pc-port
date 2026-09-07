"""Extend native startup services with independently checked reader/writer-lock interfaces."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));old=Path('local/runtime/direct-memory-contract-v1');contract=read(old/'contract.json');imports=read('local/runtime/registry-v7-memory-repeat/imports.json');source=Path('local/cfg/startup-recovery-v31-conditional-repeat');db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h,path=db.execute('select hash,path from module where name=?',('eboot.bin',)).fetchone();assert sha(path)==h;im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);checked=[]
for window in read('local/cfg/ghidra-startup-rwlock-v1/eboot.bin/ghidra.json'):
 for row in window['instructions']:
  raw=im.at_va(row['rva'],row['length']);assert raw.hex()==row['bytes'];ins=next(decoder.disasm(raw,row['rva'],count=1));assert ins.size==row['length'];checked.append(dict(**row,capstone=ins.mnemonic+' '+ins.op_str))
by={r['rva']:r for r in checked}
for at,target in [(0x207f2d3,0x2bc0cd8),(0x207f418,0x2bc0cf8),(0x207f688,0x2bc0d28),(0x207b7d7,0x2bc0ca8)]:assert by[at]['targets']==[target]
services={'6ULAa0fq4jA':'rwlock_init','mqdNorrB+gI':'rwlock_wrlock','Ox9i0c7L5w0':'rwlock_rdlock','+L98PIbGttk':'rwlock_unlock'};bindings=contract['bindings'][:]
for nid,handler in services.items():
 canonical=next(r for r in imports if r.get('canonical') and r['nid']==nid and r['library']==r['module']=='libkernel');assert canonical['library_version']==1 and canonical['module_version']==257 and not canonical['compiled_export']
 for imp in imports:
  if imp['pc']==canonical['pc'] or imp.get('canonical_service_pc')==canonical['pc']:
   assert imp['nid']==nid and imp['library']==imp['module']=='libkernel' and not imp['compiled_export'];bindings.append(dict(pc=imp['pc'],canonical_pc=canonical['pc'],handler=handler,nid=nid,library='libkernel',library_version=1,module='libkernel',module_version=257))
bindings.sort(key=lambda r:r['pc']);assert len(bindings)==len({r['pc'] for r in bindings});one=read('local/runtime/rwlock-v1/summary.json');two=read('local/runtime/rwlock-v2-repeat/summary.json');assert one==two and two['positive']['lifecycles']==4096 and two['positive']['writer_increments']==1536
ref=read('local/references/rwlock-v1/reference.json');assert sha('local/references/rwlock-v1/thr_rwlock.c')==ref['sha256']
assert by[0x207f2cf]['bytes']=='31f6' and by[0x207f2d1]['bytes']=='31d2' and by[0x207f2cb]['bytes']=='488d7b08'
contract.update(status='bounded native reader/writer-lock interfaces checked',parent_contract_sha256=sha(old/'contract.json'),bindings=bindings,rwlock_services=True,rwlock_live_limit=65536,rwlock_identifier_range=[0x73000000000,0x73100000000],rwlock_checked_instructions=len(checked),rwlock_ghidra_sha256=sha('local/cfg/ghidra-startup-rwlock-v1/eboot.bin/ghidra.json'),rwlock_authored_sha256=sha('local/runtime/rwlock-v2-repeat/summary.json'),rwlock_reference=ref,rwlock_open_group_reference='https://pubs.opengroup.org/onlinepubs/7908799/xsh/pthread_rwlock_rdlock.html',rwlock_baseline_reference_sha256=sha('external/shadPS4/src/core/libraries/kernel/threads/rwlock.cpp'))
contract['limitations']+=['Reader/writer locks use native opaque identifiers and shared-reader/exclusive-writer ownership. This does not establish a guest-readable private layout.','Only explicit default-attribute unnamed initialization is supported. Static, named, attribute, timed and priority/process-shared behavior remain unimplemented.','Writer preference with admission for recursive readers is an explicit native scheduling policy, not a console observation. Native limits and invalid/deadlock diagnostics are implementation policies.','Initialization, read, write and unlock identities are bound; destruction and try operations are authored-tested but unbound pending reached caller evidence.']
write_json(a.out/'checked-instructions.json',checked);write_json(a.out/'contract.json',contract);print(json.dumps(dict(status=contract['status'],bindings=len(bindings),instructions=len(checked),authored=two['positive'])),flush=True)
