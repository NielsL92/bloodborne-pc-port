"""Independently characterize x87 data-pointer updates by memory operand form."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=['fld tbyte ptr [r9]','fstp tbyte ptr [r9]','fld dword ptr [r9]','fld qword ptr [r9]','fild qword ptr [r9]','fstp dword ptr [r9]','fstp qword ptr [r9]','fisttp qword ptr [r9]','fadd qword ptr [r9]','fsub dword ptr [r9]']
assembly=['.intel_syntax noprefix','.text'];header=[]
for n,instruction in enumerate(cases):
 assembly.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]',instruction,'fxsave64 [rdx]','fxrstor64 [r8]','ret']);header.append(f'extern "C" void hw_{n}(const void*,void*,void*,void*);')
header.append('static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};')
(out/'hardware.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');(out/'pointer-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');write_json(out/'specs.json',cases)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/I'+str(out),'/c',ROOT/'native/semantics/x87_pointer_update_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert len(rows)==11
summary=dict(status='authored hardware data-pointer characterization complete',cpu=rows[0],groups=rows[1:],raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),source_sha256=sha(ROOT/'native/semantics/x87_pointer_update_probe.cpp'),limitations='Hardware-only authored inputs, no Remill, AOT semantic helper, SoftFloat, game bytes or SEH import path. CPUID and observed per-form updates are separate evidence; they do not establish AMD Jaguar behavior.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
