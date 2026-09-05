"""Build and execute authored VEX blend or reciprocal-square-root contracts."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('family',choices=('blend','rsqrt'));p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
authored=['.intel_syntax noprefix','.text'];hardware=['.intel_syntax noprefix','.text'];header=[];names=[];hw_names=[];specs=[]
operations=[('vblendvps',4),('vblendvpd',8),('vpblendvb',1)] if a.family=='blend' else [('vrsqrtps',4)]
for op,element in operations:
 for width in (16,32):
  prefix='xmm' if width==16 else 'ymm'
  for mode in range(5 if a.family=='blend' else 3):
   mem=mode==(4 if a.family=='blend' else 2)
   dest=([0,1,2,3,0] if a.family=='blend' else [0,2,0])[mode]
   n=len(specs);pc=0x100040000+n*16;name=f'sub_{pc:x}';hw=f'hw_{n}';names.append(name);hw_names.append(hw)
   header.extend([f'extern "C" Memory* {name}(State*,uint64_t,Memory*);',f'extern "C" void {hw}(const void*,void*,const void*);'])
   def instruction(pointer):
    second=f'{prefix}word ptr [{pointer}]' if mem else prefix+'2'
    return f'{op} {prefix}{dest}, {prefix}1, {second}, {prefix}3' if a.family=='blend' else f'{op} {prefix}{dest}, {second}'
   authored.extend([f'.org {n*16}',instruction('rdi'),'ret'])
   hardware.extend([f'.globl {hw}',hw+':',*[f'vmovdqu ymm{r}, ymmword ptr [rcx+{r*32}]' for r in range(4)],instruction('r8'),*[f'vmovdqu ymmword ptr [rdx+{r*32}], ymm{r}' for r in range(4)],'vzeroupper','ret'])
   specs.append(dict(operation=op,width=width,destination=dest,memory=mem,element_bytes=element,logical_pc=pc))
header.extend(['static Lifted lifted[]={'+','.join(names)+'};','static Hardware hardware[]={'+','.join(hw_names)+'};','static Spec specs[]={'+','.join('{'+f"{r['width']},{r['destination']},{int(r['memory'])},{r['element_bytes']},{hex(r['logical_pc'])}"+'}' for r in specs)+'};'])
(out/'vector-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(authored)+'\n',encoding='utf-8');(out/'hardware.s').write_text('\n'.join(hardware)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
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
 ins=list(decoder.disasm(text[n*16:n*16+16],r['logical_pc'],count=2));assert [i.mnemonic for i in ins]==[r['operation'],'ret']
 rows.extend(dict(address=i.address,bytes=i.bytes.hex()) for i in ins)
write_json(out/'input.json',dict(roots=[r['logical_pc'] for r in specs],instructions=rows))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('hardware',[LLVM/'bin/clang.exe','-c',out/'hardware.s','-o',out/'hardware.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-avx2','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/f'native/semantics/{a.family}_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'hardware.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe']);result=json.loads((out/'execute.stdout').read_text());assert result['status']=='pass'
write_json(out/'summary.json',dict(status='authored '+a.family+' checks pass',result=result,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),input_sha256=sha(out/'input.json'),fixture_sha256=sha(out/'fixture.exe'),limitations='Authored AOT only; host hardware and independent contract reference. No game CPU execution. No assertion of AMD Jaguar bit-exact approximation results.'))
print(json.dumps(result),flush=True)
