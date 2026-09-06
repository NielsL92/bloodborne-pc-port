"""Authored missing-transfer provenance and hypercall return contracts."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
bodies=[[(0,'e91b000000')],[(0,'b86f000000')],[(0,'85c9'),(2,'741c'),(4,'eb1a')],[(0,'ffc9'),(2,'75fc'),(4,'eb1a')],[(0,'e83b000000'),(64,'b84d010000'),(69,'c3')],[(0,'85c9'),(2,'7405'),(4,'b86f000000')],[(0,'cc'),(1,'b86f000000'),(6,'c3')]]
roots=[];rows=[];assembly=['.intel_syntax noprefix','.text'];header=[]
for n,body in enumerate(bodies):
 pc=0x1000b0000+n*256;roots.append(pc);rows += [dict(address=pc+offset,bytes=code) for offset,code in body];header += [f'extern "C" Memory* sub_{pc:x}(State*,uint64_t,Memory*);']
 if n==4:roots.append(pc+64)
 if n==6:continue # Do not execute INT3 hardware or system services.
 target=32 if n in [0,2,3] else (9 if n==5 else 5);label=f'body_{n}';assembly += ['.p2align 4',f'.globl hw_{n}',f'hw_{n}:','push r8','popfq','mov r9, rdx','mov eax, 0x12345678',f'{label}:']
 for offset,code in body:
  if offset>=64:continue
  assembly += [f'.org {label}+{offset}','.byte '+','.join('0x'+code[i:i+2] for i in range(0,len(code),2))]
 assembly += [f'.org {label}+{target}','pushfq','pop rdx','mov [r9], rdx','ret']
 if n==4:assembly += [f'.org {label}+64','mov eax, 333','ret']
 header += [f'extern "C" uint64_t hw_{n}(uint64_t,uint64_t*,uint64_t);']
header += ['static Lifted entries[]={'+','.join(f'sub_{0x1000b0000+n*256:x}' for n in range(7))+'};','static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(6))+'};']
(out/'exit-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');write_json(out/'input.json',dict(roots=sorted(roots),instructions=rows))
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/sparse_lift/exit_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')]);run('execute',[out/'fixture.exe']);result=json.loads((out/'execute.stdout').read_text(encoding='utf-8'));assert result['status']=='pass'
write_json(out/'summary.json',dict(status='authored transfer and hypercall provenance checks pass',result=result,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),artifact_sha256={name:sha(out/name) for name in ['input.json','audit.json','function.bc','function.obj','execute.stdout']},limitations='Authored AOT and six hardware byte sequences only. Hypercall response is mocked; no host INT3, service implementation, native guest unwind or game execution.'));print(json.dumps(result),flush=True)
