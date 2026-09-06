"""Expand masked x87 stack/control and special-value differential checks."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args()
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=[('push-one',['fld1']),('push-zero',['fldz']),('push-pair',['fld1','fldz']),('exchange-pop',['fld1','fldz','fxch st(1)','fstp st(0)']),('initialize',['fninit']),('load-control',['fldcw word ptr [ARG]']),('store-control',['fnstcw word ptr [ARG]']),('pop',['fstp st(0)']),('compare-pop',['fucomip st(0), st(1)']),('store-status',['fnstsw word ptr [ARG]']),('exchange-one',['fxch st(1)']),('exchange-seven',['fxch st(7)']),('pop-to-one',['fstp st(1)']),('pop-to-seven',['fstp st(7)']),('compare-one',['fucomi st(0), st(1)']),('compare-seven',['fucomi st(0), st(7)']),('compare-pop-seven',['fucomip st(0), st(7)']),('status-ax',['fnstsw ax']),('wait',['fwait'])]
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text','.globl save_host','save_host:','fxsave64 [rcx]','ret','.globl restore_host','restore_host:','fxrstor64 [rcx]','ret'];header=[];specs=[]
for n,(name,instructions) in enumerate(cases):
 pc=0x100060000+n*64
 authored.extend([f'.org {n*64}',*[i.replace('ARG','rdi') for i in instructions],'ret'])
 hardware.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]','push qword ptr [rcx+512]','popfq',*[i.replace('ARG','r9') for i in instructions],'pushfq','pop r10','mov [rdx+544],r10','mov [rdx+552],rax','fxsave64 [rdx]','fnstenv [rdx+512]','fxrstor64 [r8]','ret'])
 header.extend([f'extern "C" Memory* sub_{pc:x}(State*,uint64_t,Memory*);',f'extern "C" void hw_{n}(const void*,void*,void*,void*);'])
 specs.append(dict(name=name,pc=pc,instructions=instructions))
header.extend(['static Lifted lifted[]={'+','.join(f'sub_{s["pc"]:x}' for s in specs)+'};','static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};','static uint64_t pcs[]={'+','.join(hex(s['pc']) for s in specs)+'};'])
(out/'x87-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(authored)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(hardware)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
blob=(out/'authored.obj').read_bytes();sections=struct.unpack_from('<H',blob,2)[0];opt=struct.unpack_from('<H',blob,16)[0];text=None
for n in range(sections):
 at=20+opt+40*n
 if blob[at:at+8].rstrip(b'\0')==b'.text':
  size,pointer=struct.unpack_from('<II',blob,at+16);text=blob[pointer:pointer+size]
assert text is not None
rows=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for n,s in enumerate(specs):
 ins=list(decoder.disasm(text[n*64:n*64+64],s['pc'],count=len(s['instructions'])+1));assert len(ins)==len(s['instructions'])+1 and ins[-1].mnemonic=='ret'
 rows.extend(dict(address=i.address,bytes=i.bytes.hex()) for i in ins)
write_json(out/'input.json',dict(roots=[s['pc'] for s in specs],instructions=rows))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/x87_stack_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
observations=[json.loads(line) for line in (out/'execute.stdout').open()];assert len(observations)==len(cases)
summary=dict(status='masked x87 expanded characterization complete',cases=sum(r['cases'] for r in observations),differing_cases=sum(r['differing_cases'] for r in observations),groups=observations,raw_sha256=sha(out/'execute.stdout'),lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),fixture_sha256=sha(out/'fixture.exe'),limitations='Authored AOT and Intel host instructions only. Masked exceptions; every occupancy and TOP, all supported precision/rounding settings, special 80-bit values and defined comparison flags. Unaffected State bytes and host controls checked. Guest IP/DP/FOP values, undefined flags, empty payloads and native unmasked fault delivery excluded. No game execution or AMD Jaguar equivalence claim.')
write_json(out/'summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='groups'}),flush=True)
