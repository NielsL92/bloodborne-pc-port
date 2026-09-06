"""Validate experimental x87 environment instruction bindings and runtime boundaries."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
cases=[('store-environment',['fnstenv [ARG]']),('load-environment',['fldenv [ARG]']),('save-legacy',['fxsave [ARG]']),('save-wide',['fxsave64 [ARG]']),('load-wait',['fldenv [ARG]','fwait']),('roundtrip',['fnstenv [ARG]','fldenv [ARG]']),('roundtrip-wait',['fnstenv [ARG]','fldenv [ARG]','fwait']),('load-control',['fldcw word ptr [ARG]'])]
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text','.globl save_host','save_host:','fxsave64 [rcx]','ret','.globl restore_host','restore_host:','fxrstor64 [rcx]','ret'];header=[];specs=[]
for n,(name,instructions) in enumerate(cases):
 pc=0x100060000+n*64
 authored.extend([f'.org {n*64}',*[i.replace('ARG','rdi') for i in instructions],'ret'])
 hardware.extend([f'.globl hw_{n}',f'hw_{n}:','fxsave64 [r8]','fxrstor64 [rcx]','fxsave64 [rdx+560]','push qword ptr [rcx+512]','popfq',f'.globl hw_{n}_start',f'hw_{n}_start:',*[part for j,i in enumerate(instructions) for part in [f'.globl hw_{n}_at_{j}',f'hw_{n}_at_{j}:',i.replace('ARG','r9')]],'pushfq','pop r10','mov [rdx+544],r10','mov [rdx+552],rax','fxsave64 [rdx]','fnstenv [rdx+512]','fxrstor64 [r8]','ret'])
 header.append(f'extern "C" char hw_{n}_start;')
 header.extend(f'extern "C" char hw_{n}_at_{j};' for j in range(len(instructions)))
 header.extend([f'extern "C" Memory* sub_{pc:x}(State*,uint64_t,Memory*);',f'extern "C" void hw_{n}(const void*,void*,void*,void*);'])
 specs.append(dict(name=name,pc=pc,instructions=instructions))
header.extend(['static Lifted lifted[]={'+','.join(f'sub_{s["pc"]:x}' for s in specs)+'};','static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(cases)))+'};','static uint64_t pcs[]={'+','.join(hex(s['pc']) for s in specs)+'};'])
header.append('static uintptr_t starts[]={'+','.join(f'uintptr_t(&hw_{n}_start)' for n in range(len(cases)))+'};')
header.append('static unsigned base_forms[]={'+','.join(map(str,range(len(cases))))+'};')
header.append('static constexpr unsigned form_count='+str(len(cases))+';')
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
rows=[];host_ips=[];guest_ips=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for n,s in enumerate(specs):
 ins=list(decoder.disasm(text[n*64:n*64+64],s['pc'],count=len(s['instructions'])+1));assert len(ins)==len(s['instructions'])+1 and ins[-1].mnemonic=='ret'
 rows.extend(dict(address=i.address,bytes=i.bytes.hex()) for i in ins)
 host_ips.extend(f'uintptr_t(&hw_{n}_at_{j})' for j in range(len(ins)-1));guest_ips.extend(i.address for i in ins[:-1])
with (out/'x87-entries.h').open('a',encoding='utf-8') as h:h.write('static uintptr_t host_ips[]={'+','.join(host_ips)+'};\nstatic uint64_t guest_ips[]={'+','.join(map(str,guest_ips))+'};\n')
write_json(out/'input.json',dict(roots=[s['pc'] for s in specs],instructions=rows))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
if a.prepare_only:
 write_json(out/'prepared.json',dict(status='authored input lifted; no execution',forms=len(cases),semantics_sha256=sha(a.semantics/'amd64_avx.bc')));raise SystemExit(0)
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/x87_image_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
observations=[json.loads(line) for line in (out/'execute.stdout').open()];assert len(observations)==len(cases)
summary=dict(status='experimental x87 image instruction characterization complete',cases=sum(r['cases'] for r in observations),differing_cases=sum(r['differing_cases'] for r in observations),groups=observations,raw_sha256=sha(out/'execute.stdout'),lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),fixture_sha256=sha(out/'fixture.exe'),limitations='Authored AOT only, with independent Intel hardware images and explicit AMD policy expectations. Runtime services select the profile, track pointer segments and validate a fully mapped RAM span. This is not a general guest memory-fault implementation or native Windows/PS4 exception delivery. No game bytes executed. Coherent x87 memory/arithmetic and MMX alias handling remain open.')
write_json(out/'summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='groups'}),flush=True)
assert summary['differing_cases']==0, 'image instruction contract differences retained in summary.json'
