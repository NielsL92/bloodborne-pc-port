"""Fail closed on MMX while retaining ordinary SSE/x87 compilation."""
import json,subprocess,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);driver=Path(sys.argv[2]).resolve();semantics=Path(sys.argv[3]).resolve();decoder=Cs(CS_ARCH_X86,CS_MODE_64)
cases=[('480f6ec0',False),('480f7ec0',False),('0ffcc1',False),('0f77',False),('0f0e',False),('0f6f00',False),('0f7f00',False),('0fe700',False),('f20fd6c1',False),('f30fd6c1',False),('0f2ac1',False),('0f2dc1',False),('660ffcc1',True),('d9e8',True),('0fae00',True)];rows=[]
for n,(code,accept) in enumerate(cases):
 folder=out/str(n);folder.mkdir();pc=0x1000b0000+n*32;decoded=list(decoder.disasm(bytes.fromhex(code),pc));assert len(decoded)==1 and decoded[0].size==len(code)//2
 write_json(folder/'input.json',dict(roots=[pc],instructions=[dict(address=pc,bytes=code),dict(address=pc+len(code)//2,bytes='c3')]))
 argv=list(map(str,[driver,folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json',semantics]))
 with (folder/'stdout').open('wb') as stdout,(folder/'stderr').open('wb') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=120)
 row=dict(bytes=code,mnemonic=decoded[0].mnemonic,operands=decoded[0].op_str,expected_accept=accept,exit_code=r.returncode,argv=argv);rows.append(row);write_json(out/'steps.json',rows);assert r.returncode==(0 if accept else 2),row
 if not accept:assert 'MMX/x87 shared-state semantics are not validated' in (folder/'stderr').read_text(encoding='utf-8')
summary=dict(status='explicit MMX rejection and non-MMX controls passed',cases=len(cases),rejected_mmx=12,accepted_controls=3,lifter_sha256=sha(driver),semantics_sha256=sha(semantics/'amd64_avx.bc'),execution='none; static authored bytes only')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
