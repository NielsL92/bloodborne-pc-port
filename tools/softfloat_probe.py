"""Compare the candidate native numeric library with authored x87 arithmetic."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('library',type=Path);p.add_argument('--characterize',action='store_true');a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=[('load32','fld dword ptr [r9]'),('load64','fld qword ptr [r9]'),('loadi64','fild qword ptr [r9]'),('store32','fstp dword ptr [r9]'),('store64','fstp qword ptr [r9]'),('storei64','fisttp qword ptr [r9]'),('add','faddp st(1), st(0)'),('sub','fsubp st(1), st(0)'),('mul','fmulp st(1), st(0)')]
assembly=['.intel_syntax noprefix','.text','.globl save_host','save_host:','fxsave64 [rcx]','ret','.globl restore_host','restore_host:','fxrstor64 [rcx]','ret'];header=[]
for n,(name,instruction) in enumerate(cases):
 assembly.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]',instruction,'fxsave64 [rdx]','fxrstor64 [r8]','ret']);header.append(f'extern "C" void hw_{n}(const void*,void*,void*,void*);')
header.append('static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};')
(out/'hardware.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');(out/'numeric-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');write_json(out/'specs.json',cases)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/DSOFTFLOAT_FAST_INT64','/DLITTLEENDIAN=1','/DTHREAD_LOCAL=thread_local','/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/I'+str(out),'/c',ROOT/'native/semantics/softfloat_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'hardware.obj',a.library.resolve(),'/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert len(rows)==10
summary=dict(status='candidate numeric library characterization complete',groups=rows,cases=sum(r['cases'] for r in rows),differing_cases=sum(r['differing_cases'] for r in rows),raw_sha256=sha(out/'execute.stdout'),library_sha256=sha(a.library),fixture_sha256=sha(out/'fixture.exe'),source_sha256=sha(ROOT/'native/semantics/softfloat_probe.cpp'),limitations='Compiled numeric C library only, not instruction interpretation or a guest execution fallback. Authored hardware supplies result bits and IEEE exception flags for masked numeric operations. x87 denormal-operand flags, C1 rounding indication, stack/tag/memory/control boundaries, noncanonical inputs and unmasked wrapped results remain outside the numeric library contract. No game bytes executed.')
write_json(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='groups'}),flush=True)
if not a.characterize:assert summary['differing_cases']==0,'numeric differences retained in summary.json'
