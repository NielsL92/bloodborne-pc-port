"""Characterize x87 environment layouts and control-word normalization."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
assembly=['.intel_syntax noprefix','.text']
for name,instructions in [('store',['fnstenv [r8]','fxsave64 [r8+32]']),('load',['fldenv [rdx]','fxsave64 [r8]','fnstenv [r8+512]']),('legacy',['fxsave [r8]','fxsave64 [r8+512]']),('control',['fldcw word ptr [rdx]','fxsave64 [r8]'])]:
 assembly.extend([f'.globl probe_{name}',f'probe_{name}:','fxsave64 [r9]','fxrstor64 [rcx]',*instructions,'fxrstor64 [r9]','ret'])
(out/'authored.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8')

def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/c',ROOT/'native/semantics/x87_layout_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').open()];assert len(rows)==98
summary=dict(status='authored x87 layout characterization complete',control_cases=rows[0],layout_cases=len(rows)-2,raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),assembly_sha256=sha(out/'authored.s'),source_sha256=sha(ROOT/'native/semantics/x87_layout_probe.cpp'),limitations='Authored Intel hardware only. Control normalization and concrete layout observations. No AOT or game CPU execution; AMD conditional pointer saves and native memory faults remain separate obligations.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
