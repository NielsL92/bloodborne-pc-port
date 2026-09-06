"""Independently isolate C1 behavior of x87 integer-flag comparisons."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
assembly=['.intel_syntax noprefix','.text'];header=[]
for form,mnemonic in enumerate(['fcomi','fcomip','fucomi','fucomip']):
 for setup in range(2):
  n=form*2+setup
  assembly.extend([f'.globl probe_{n}',f'probe_{n}:','fxsave64 [r9]','fninit'])
  if setup:assembly.extend(['fld tbyte ptr [rdx+16]','fld tbyte ptr [rdx]'])
  assembly.extend(['sub rsp,32','fnstenv [rsp]','mov ax,word ptr [rcx+2]','or word ptr [rsp+4],ax','fldenv [rsp]','add rsp,32','fnstsw word ptr [r8+528]','fldcw word ptr [rcx]','push qword ptr [rcx+8]','popfq','pushfq','pop r10','mov [r8+512],r10',f'{mnemonic} st(0), st(1)','pushfq','pop r10','mov [r8+520],r10','fxsave64 [r8]','fnclex','fxrstor64 [r9]','ret'])
  header.append(f'extern "C" void probe_{n}(const void*,const void*,void*,void*);')
header.append('static Probe probes[]={'+','.join(f'probe_{n}' for n in range(8))+'};')
(out/'entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8')

def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/I'+str(out),'/c',ROOT/'native/semantics/x87_compare_c1_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')])
run('disassemble',[LLVM/'bin/llvm-objdump.exe','-d','--x86-asm-syntax=intel',out/'authored.obj'])
run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').open()];assert len(rows)==131072
assert all((r['initial_status']&0x200)==r['c1']*0x200 for r in rows)
differences=[r for r in rows if (r['status']&0x200)!=(0 if r['status']&0x40 else r['c1']*0x200)]
assert not differences, differences[:5]
invalid=[r for r in rows if (r['status']&1) and not(r['control']&1)]
summary=dict(status='independent authored hardware comparison completed',cases=len(rows),c1_differences=len(differences),stack_cases=sum(bool(r['status']&0x40) for r in rows),preserved_c1_cases=sum(bool(r['status']&0x200) for r in rows),unmasked_invalid_cases=len(invalid),unmasked_invalid_unordered_flags=sum((r['after']&0x45)==0x45 for r in invalid),unmasked_invalid_flags_changed=sum((r['before']&0x45)!=(r['after']&0x45) for r in invalid),raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),assembly_sha256=sha(out/'authored.s'),source_sha256=sha(ROOT/'native/semantics/x87_compare_c1_probe.cpp'),limitations='Authored native hardware only. FNINIT/FLD80 and a local 28-byte environment image initialize each case with independently selected C1; immediate PUSHFQ captures flags before any waiting instruction. No Remill, AOT, FXRSTOR-imported guest values or SEH in comparison path. Host backup is restored before returning. Intel host observation does not settle AMD Jaguar semantics.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
