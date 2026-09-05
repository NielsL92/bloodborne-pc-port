"""Build and execute authored BMI forms against independent references, AOT only."""
import argparse,json,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();rows=[];roots=[];assembly=['.intel_syntax noprefix','.text'];header=[];names=[];hardware=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for n in range(8):
 width=64 if n&1 else 32;mem=bool(n&2);mnemonic='blsi' if n>=4 else 'blsr';pc=0x100010000+n*0x100
 raw=bytes([0xc4,0xe2,0xf8 if width==64 else 0x78,0xf3,(0x18 if n>=4 else 8)+7+(0 if mem else 0xc0)])
 ins=list(decoder.disasm(raw,pc));assert len(ins)==1 and ins[0].mnemonic==mnemonic and ins[0].size==5
 roots.append(pc);rows.extend([dict(address=pc,bytes=raw.hex()),dict(address=pc+5,bytes='c3')]);names.append(f'sub_{pc:x}');hardware.append(f'hw_{n}')
 header.append(f'extern "C" Memory* {names[-1]}(State*,uint64_t,Memory*);');header.append(f'extern "C" uint64_t hw_{n}(uint64_t,uint64_t*);')
 operand=('qword ptr [rcx]' if width==64 else 'dword ptr [rcx]') if mem else ('rcx' if width==64 else 'ecx')
 assembly.extend([f'.globl hw_{n}',f'hw_{n}:',f'{mnemonic} '+('rax' if width==64 else 'eax')+', '+operand,'pushfq','pop r8','mov qword ptr [rdx], r8','ret'])
header += ['static Lifted lifted[]={'+','.join(names)+'};','static Hardware hardware[]={'+','.join(hardware)+'};','static uint64_t addresses[]={'+','.join(hex(pc) for pc in roots)+'};']
(out/'bmi-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');write_json(out/'input.json',dict(roots=roots,instructions=rows))
steps=[]
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=120)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-bmi','/clang:-mno-bmi2','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/bmi_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
result=json.loads((out/'execute.stdout').read_text());assert result['aot_cases']==34816
write_json(out/'summary.json',dict(status='authored BMI semantics checks pass',result=result,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),fixture_sha256=sha(out/'fixture.exe'),input_sha256=sha(out/'input.json'),limitations='Authored BMI forms on this Intel CPU; defined flag and full state/memory checks only. AF/PF undefined outputs are excluded. No original game CPU execution or exception/runtime validation.'))
print(json.dumps(result),flush=True)
