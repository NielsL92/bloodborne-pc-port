"""Characterize authored DIV/IDIV against Python integers and hardware."""
import argparse,itertools,json,random,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--expect-mismatch',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text'];header=[];specs=[]
for signed in [False,True]:
 for width in [8,16,32,64]:
  for operand in range(4):
   n=len(specs);pc=0x100080000+n*16;op='idiv' if signed else 'div';low={8:'al',16:'ax',32:'eax',64:'rax'}[width];high={8:'ah',16:'dx',32:'edx',64:'rdx'}[width];other={8:'cl',16:'cx',32:'ecx',64:'rcx'}[width];size={8:'byte',16:'word',32:'dword',64:'qword'}[width]
   def instruction(pointer):return op+' '+[other,low,high,size+f' ptr [{pointer}]'][operand]
   authored += [f'.org {n*16}',instruction('rdi'),'ret']
   hw=f'hw_{n}';site=f'hw_site_{n}';hardware += [f'.globl {hw}',hw+':','mov r9, rcx','mov r10, rdx','mov rax, qword ptr [r9]','mov rdx, qword ptr [r9+8]','mov rcx, qword ptr [r9+16]','push qword ptr [r9+32]','popfq',f'.globl {site}',site+':',instruction('r8'),'mov qword ptr [r10], rax','mov qword ptr [r10+8], rdx','mov qword ptr [r10+16], rcx','pushfq','pop r11','mov qword ptr [r10+24], r11','ret']
   header += [f'extern "C" Memory* sub_{pc:x}(State*,uint64_t,Memory*);',f'extern "C" void {hw}(const void*,void*,const void*);',f'extern "C" char {site};']
   specs.append(dict(operation=op,signed=signed,width=width,operand=operand,pc=pc))
header += ['static Lifted lifted[]={'+','.join(f"sub_{s['pc']:x}" for s in specs)+'};','static Hardware hardware[]={'+','.join(f'hw_{i}' for i in range(len(specs)))+'};','static const void* hardware_sites[]={'+','.join(f'&hw_site_{i}' for i in range(len(specs)))+'};','static Spec specs[]={'+','.join('{'+f"{s['width']},{s['operand']},{int(s['signed'])},{s['pc']}ULL"+'}' for s in specs)+'};']
(out/'divide-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(authored)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(hardware)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
rng=random.Random(0x46f289fab710);counts=[];faults={0:0,1:0,2:0};u64=(1<<64)-1
for form,s in enumerate(specs):
 w=s['width'];mask=(1<<w)-1;sign=1<<(w-1);values=[0,1,2,3,4,7,15,sign-2,sign-1,sign,sign+1,sign+2,mask-3,mask-2,mask-1,mask];triples=list(itertools.product(values,repeat=3))
 triples += [(rng.getrandbits(w),rng.getrandbits(w),rng.getrandbits(w)) for _ in range(4096)]
 for _ in range(2048):
  divisor=rng.getrandbits(w) or 1;q=rng.getrandbits(w);r=rng.randrange(divisor);lhs=(q*divisor+r)&((1<<(w*2))-1);triples.append((lhs&mask,lhs>>w,divisor))
 with (out/f'cases-{form:02d}.bin').open('wb') as stream:
  for trial,(lo,hi,divisor) in enumerate(triples):
   ra=((0xa58e7d6c5b4a3900&~((1<<16)-1))|lo|(hi<<8)) if w==8 else ((0xa58e7d6c5b4a3900&~mask)|lo)
   rd=(0x63d287419acbe500&~mask)|hi;rc=(0x731cf4e85a9b0200&~mask)|divisor
   rhs=[rc&mask,ra&mask,(ra>>8)&mask if w==8 else rd&mask,divisor][s['operand']];lhs=lo|(hi<<w);fault=0;expected_ra=ra;expected_rd=rd
   if not rhs:fault=1
   else:
    if s['signed']:
     dividend=lhs-(1<<(2*w)) if lhs&(1<<(2*w-1)) else lhs;divisor_signed=rhs-(1<<w) if rhs&sign else rhs;q=abs(dividend)//abs(divisor_signed);q=-q if (dividend<0)!=(divisor_signed<0) else q;r=dividend-q*divisor_signed;fault=2 if q< -sign or q>=sign else 0
    else:q,r=divmod(lhs,rhs);fault=2 if q>mask else 0
    if not fault:
     if w==8:expected_ra=(ra&~0xffff)|(q&255)|((r&255)<<8)
     else:expected_ra=(q&mask)|((ra&~mask) if w==16 else 0);expected_rd=(r&mask)|((rd&~mask) if w==16 else 0)
   n=trial&63;flags=0x202|(n&1)|((n&2)<<1)|((n&4)<<2)|((n&8)<<3)|((n&16)<<3)|((n&32)<<6)
   stream.write(struct.pack('<8Q',ra,rd,rc,rhs,flags,expected_ra&u64,expected_rd&u64,fault));faults[fault]+=1
 counts.append(len(triples))
write_json(out/'oracle.json',dict(method='Python arbitrary precision signed/unsigned quotient and remainder; no native arithmetic helper in this oracle',cases_per_form=counts,outcomes=faults,case_sha256={f'cases-{n:02d}.bin':sha(out/f'cases-{n:02d}.bin') for n in range(len(specs))}))
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
blob=(out/'authored.obj').read_bytes();machine,sections=struct.unpack_from('<HH',blob);assert machine==0x8664;opt=struct.unpack_from('<H',blob,16)[0];text=None
for n in range(sections):
 at=20+opt+40*n
 if blob[at:at+8].rstrip(b'\0')==b'.text':
  size,pointer=struct.unpack_from('<II',blob,at+16);text=blob[pointer:pointer+size]
assert text is not None
rows=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for n,s in enumerate(specs):
 ins=list(decoder.disasm(text[n*16:n*16+16],s['pc'],count=2));assert [i.mnemonic for i in ins]==[s['operation'],'ret'];rows.extend(dict(address=i.address,bytes=i.bytes.hex()) for i in ins)
write_json(out/'input.json',dict(roots=[s['pc'] for s in specs],instructions=rows))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-avx2','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/divide_fixture.cpp','/Fo'+str(out/'fixture.obj')])
builtins=LLVM/'lib/clang/21/lib/windows/clang_rt.builtins-x86_64.lib'
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj',builtins,'/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe',out]);lines=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];result=lines[-1];assert result['status']=='characterized';assert (result['mismatched_cases']>0)==a.expect_mismatch
write_json(out/'summary.json',dict(status='counterexamples reproduced' if a.expect_mismatch else 'authored DIV/IDIV contract passes',result=result,builtins_sha256=sha(builtins),oracle_sha256=sha(out/'oracle.json'),expect_mismatch=a.expect_mismatch,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),input_sha256=sha(out/'input.json'),bitcode_sha256=sha(out/'function.bc'),object_sha256=sha(out/'function.obj'),fixture_sha256=sha(out/'fixture.exe'),raw_sha256=sha(out/'execute.stdout'),limitations='Authored Python-integer/hardware/AOT checks only. Arithmetic flags are undefined on successful division and excluded there. Fault state/PC, result registers, memory and host state are checked; no game execution or PS4 fault delivery.'))
print(json.dumps(result),flush=True)
