"""Exercise every VSHUFPS immediate, lane width, alias and memory form via authored AOT."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment()
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text'];header=[];lift_names=[];hw_names=[];specs=[];steps=[]
for form in range(8):
 width=32 if form>=4 else 16;mode=form%4;dest=1 if mode==1 else 2 if mode==2 else 0;mem=mode==3;prefix='ymm' if width==32 else 'xmm'
 for imm in range(256):
  n=form*256+imm;pc=0x100030000+n*16;name=f'sub_{pc:x}';hw=f'hw_{n}';lift_names.append(name);hw_names.append(hw)
  header.extend([f'extern "C" Memory* {name}(State*,uint64_t,Memory*);',f'extern "C" void {hw}(const void*,void*,const void*);'])
  authored_operand=f'{prefix}word ptr [rdi]' if mem else prefix+'2';native_operand=f'{prefix}word ptr [r8]' if mem else prefix+'2'
  authored.extend([f'.org {n*16}',f'vshufps {prefix}{dest}, {prefix}1, {authored_operand}, {imm}','ret'])
  hardware.extend([f'.globl {hw}',hw+':','vmovdqu ymm0, ymmword ptr [rcx]','vmovdqu ymm1, ymmword ptr [rcx+32]','vmovdqu ymm2, ymmword ptr [rcx+64]',f'vshufps {prefix}{dest}, {prefix}1, {native_operand}, {imm}','vmovdqu ymmword ptr [rdx], ymm0','vmovdqu ymmword ptr [rdx+32], ymm1','vmovdqu ymmword ptr [rdx+64], ymm2','vzeroupper','ret'])
  specs.append(dict(form=form,immediate=imm,logical_pc=pc,width=width,destination=dest,memory=mem))
(out/'authored.s').write_text('\n'.join(authored)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(hardware)+'\n',encoding='utf-8')
header.extend(['static Lifted lifted[]={'+','.join(lift_names)+'};','static Hardware hardware[]={'+','.join(hw_names)+'};','static uint64_t addresses[]={'+','.join(hex(r['logical_pc']) for r in specs)+'};'])
(out/'shuffle-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
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
for n,r in enumerate(specs):
 ins=list(decoder.disasm(text[n*16:n*16+16],r['logical_pc'],count=2));assert [i.mnemonic for i in ins]==['vshufps','ret']
 rows.extend(dict(address=i.address,bytes=i.bytes.hex()) for i in ins)
write_json(out/'input.json',dict(roots=[r['logical_pc'] for r in specs],instructions=rows))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-avx2','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/semantics/shuffle_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe']);result=json.loads((out/'execute.stdout').read_text());assert result['aot_cases']==32768
write_json(out/'summary.json',dict(status='authored VSHUFPS semantics checks pass',result=result,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),input_sha256=sha(out/'input.json'),fixture_sha256=sha(out/'fixture.exe'),limitations='Authored AOT and independent hardware/reference checks of every immediate, both VEX widths, destination aliases, guarded memory, full State and upper-YMM clearing. Storage for disabled AVX512 is preserved. No game CPU execution or complete SIMD/runtime claim.'))
print(json.dumps(result),flush=True)
