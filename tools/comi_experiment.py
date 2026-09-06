"""Characterize authored COMI/UCOMI hardware versus AOT, preserving counterexamples."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--expect-mismatch',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text'];header=[];specs=[]
for op in ['comiss','comisd','ucomiss','ucomisd','vcomiss','vcomisd','vucomiss','vucomisd']:
 for mem in [False,True]:
  n=len(specs);pc=0x100070000+n*16;width=8 if op.endswith('sd') else 4;name=f'sub_{pc:x}';hw=f'hw_{n}';site=f'hw_site_{n}'
  def instruction(pointer):return op+' xmm1, '+(('qword' if width==8 else 'dword')+f' ptr [{pointer}]' if mem else 'xmm2')
  authored += [f'.org {n*16}',instruction('rdi'),'ret']
  hardware += [f'.globl {hw}',hw+':',*[f'vmovdqu ymm{r}, ymmword ptr [rcx+{r*32}]' for r in range(4)],'push qword ptr [rcx+128]','popfq',f'.globl {site}',site+':',instruction('r8'),'pushfq','pop rax','mov qword ptr [rdx+128], rax',*[f'vmovdqu ymmword ptr [rdx+{r*32}], ymm{r}' for r in range(4)],'vzeroupper','ret']
  header += [f'extern "C" Memory* {name}(State*,uint64_t,Memory*);',f'extern "C" void {hw}(const void*,void*,const void*);',f'extern "C" char {site};']
  specs.append(dict(operation=op,width=width,memory=mem,unordered='ucomi' in op,pc=pc))
header += ['static Lifted lifted[]={'+','.join(f"sub_{s['pc']:x}" for s in specs)+'};','static Hardware hardware[]={'+','.join(f'hw_{i}' for i in range(len(specs)))+'};','static const void* hardware_sites[]={'+','.join(f'&hw_site_{i}' for i in range(len(specs)))+'};','static Spec specs[]={'+','.join('{'+f"{s['width']},{int(s['memory'])},{int(s['unordered'])},{s['pc']}ULL"+'}' for s in specs)+'};']
(out/'comi-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(authored)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(hardware)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
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
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-avx2','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/comi_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe']);lines=[json.loads(line) for line in (out/'execute.stdout').read_text(encoding='utf-8').splitlines()];result=lines[-1];assert result['status']=='characterized';assert (result['mismatched_cases']>0)==a.expect_mismatch
write_json(out/'summary.json',dict(status='counterexamples reproduced' if a.expect_mismatch else 'authored COMI/UCOMI contract passes',result=result,expect_mismatch=a.expect_mismatch,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),input_sha256=sha(out/'input.json'),bitcode_sha256=sha(out/'function.bc'),object_sha256=sha(out/'function.obj'),fixture_sha256=sha(out/'fixture.exe'),raw_sha256=sha(out/'execute.stdout'),limitations='Authored host hardware and AOT only. Full native State, memory, explicit faults, flags, MXCSR and host isolation checked; no game execution or PS4 exception-delivery claim.'))
print(json.dumps(result),flush=True)
