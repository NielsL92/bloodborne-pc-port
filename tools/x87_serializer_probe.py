"""Compare canonical state-image helpers against authored hardware serializers."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
assembly=['.intel_syntax noprefix','.text']
for name,instructions in [('store',['fnstenv [r8]','fxsave64 [r8+32]']),('load',['fldenv [rdx]','fxsave64 [r8]','fnstenv [r8+512]']),('legacy',['fxsave [r8]','fxsave64 [r8+512]']),('control',['fldcw word ptr [rdx]','fxsave64 [r8]']),('wide',['fxsave64 [r8]'])]:
 assembly.extend([f'.globl probe_{name}',f'probe_{name}:','fxsave64 [r9]','fxrstor64 [rcx]',*instructions,'fxrstor64 [r9]','ret'])
(out/'authored.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8')

def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/semantics/x87_serializer_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
summary=json.loads((out/'execute.stdout').read_text());assert summary['differences']==0
summary.update(status='canonical x87 state-image helpers match checked hardware fields',raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),assembly_sha256=sha(out/'authored.s'),source_sha256=sha(ROOT/'native/semantics/x87_serializer_probe.cpp'),serializer_sha256=sha(ROOT/'native/semantics/x87_environment.h'),limitations='Data helpers only, no startup selectors added. Intel calibration profile checked against hardware. AMD exception-only pointer preservation checked as an explicit documented policy, not AMD execution. Host upper-pointer loss is counted separately only when both pointers are truncated exactly to 32 bits and every other saved byte matches. Full canonical pointer encodings are checked independently; see x87-pointer-probe-v1. Caller memory alignment, permission and waiting faults remain outside these pure helpers. MMX/x87 aliasing and guest pointer metadata integration remain open.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
