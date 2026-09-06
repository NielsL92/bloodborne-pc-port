"""Independently observe x87 store completion and flags before a later wait."""
import json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=['fst dword ptr [r9]','fst qword ptr [r9]','fstp dword ptr [r9]','fstp qword ptr [r9]','fisttp word ptr [r9]','fisttp dword ptr [r9]','fisttp qword ptr [r9]'];assembly=['.intel_syntax noprefix','.text'];header=[]
for n,ins in enumerate(cases):
 assembly.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]',ins,'fxsave64 [rdx]','fnclex','fxrstor64 [r8]','ret']);header.append(f'extern "C" void hw_{n}(const void*,void*,void*,void*);')
header.append('static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};');(out/'entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');write_json(out/'specs.json',cases)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/I'+str(out),'/c',ROOT/'native/semantics/x87_store_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'hardware.obj',out/'fixture.obj','/Fe'+str(out/'fixture.exe')]);run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];groups=[]
for form in range(7):
 group=[r for r in rows if r['form']==form];unmasked=[r for r in group if r['status']&~r['control']&63];groups.append(dict(form=form,cases=len(group),new_unmasked_cases=len(unmasked),unmasked_store_cases=sum(r['stored'] for r in unmasked),unmasked_pop_cases=sum(r['top']!=0 for r in unmasked),unmasked_by_flags={str(flags):dict(cases=len(g),stored=sum(r['stored'] for r in g),popped=sum(r['top']!=0 for r in g)) for flags in sorted(set(r['status']&~r['control']&63 for r in unmasked)) if (g:=[r for r in unmasked if r['status']&~r['control']&63==flags])}))
summary=dict(status='independent authored x87 store observations retained',cases=len(rows),groups=groups,raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),source_sha256=sha(ROOT/'native/semantics/x87_store_probe.cpp'),limitations='Authored native hardware only, before a later waiting instruction. FXRSTOR supplies exact source/control/status/tag state. No Remill, SoftFloat, AOT or SEH comparison path. Intel observations do not establish AMD Jaguar behavior.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
