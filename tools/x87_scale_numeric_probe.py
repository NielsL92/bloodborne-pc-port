"""Compare scoped arithmetic helpers with independent authored hardware."""
import json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
library=Path(sys.argv[2]).resolve();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=['fscale'];assembly=['.intel_syntax noprefix','.text','.globl save_host','save_host:','fxsave64 [rcx]','ret'];header=[]
for n,ins in enumerate(cases):
 assembly.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]',ins,'fxsave64 [rdx]','fnclex','fxrstor64 [r8]','ret']);header.append(f'extern "C" void hw_{n}(const void*,void*,void*);')
header.append('static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};');(out/'entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');write_json(out/'specs.json',cases)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/I'+str(out),'/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/c',ROOT/'native/semantics/x87_scale_numeric_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('numeric',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/c',ROOT/'native/semantics/x87_numeric.cpp','/Fo'+str(out/'numeric.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'hardware.obj',out/'fixture.obj',out/'numeric.obj',library,'/Fe'+str(out/'fixture.exe')]);run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert len(rows)==1
summary=dict(status='scoped FSCALE numeric characterization retained',cases=sum(r['cases'] for r in rows),differing_cases=sum(r['differing_cases'] for r in rows),reserved_control_cases=sum(r['reserved_control_cases'] for r in rows),groups=rows,raw_sha256=sha(out/'execute.stdout'),library_sha256=sha(library),fixture_sha256=sha(out/'fixture.exe'),source_sha256=sha(ROOT/'native/semantics/x87_scale_numeric_fixture.cpp'),limitations='Authored hardware versus ordinary native numeric helpers only; no AOT or game execution. All precision-control encodings compare raw results/flags/C1 and scoped library/host state. FSCALE ignores PC. Instruction stack/tag/control boundaries remain separate.')
write_json(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='groups'}),flush=True);assert summary['differing_cases']==0
