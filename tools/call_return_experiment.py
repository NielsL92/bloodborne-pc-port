"""Authored call-return integrity characterization for the sparse compiler."""
import argparse,json,struct,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--expect-unchecked',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];assembly=['.intel_syntax noprefix','.text'];header=[];specs=[]
for mode in range(3):
 for indirect in [False,True]:
  n=len(specs);pc=0x100090000+n*256;length=2 if indirect else 5;delta=32-length;prefix=f'case_{n}';assembly += ['.p2align 8',f'.globl hw_{n}',f'hw_{n}:',f'{prefix}:','call rcx' if indirect else f'call {prefix}_helper','mov eax, 111','ret',f'.org {prefix}+32','mov eax, 222','ret',f'.org {prefix}+64',f'{prefix}_helper:']
  if mode==1:assembly += [f'add qword ptr [rsp], {delta}']
  assembly += ['ret'];header += [f'extern "C" uint64_t hw_{n}(uint64_t);']
  for offset in [0,length,32,64]:header += [f'extern "C" Memory* sub_{pc+offset:x}(State*,uint64_t,Memory*);']
  specs.append(dict(pc=pc,mode=mode,indirect=indirect,length=length,delta=delta))
header += ['static Lifted entries[]={'+','.join(f"sub_{s['pc']:x}" for s in specs)+'};','static Lifted helpers[]={'+','.join(f"sub_{s['pc']+64:x}" for s in specs)+'};','static Hardware hardware[]={'+','.join(f'hw_{n}' for n in range(len(specs)))+'};','static Spec specs[]={'+','.join('{'+f"{s['pc']}ULL,{s['mode']},{int(s['indirect'])},{s['length']},{s['delta']}"+'}' for s in specs)+'};']
assembly += ['.p2align 8','.globl hw_getpc','hw_getpc:','call 1f','1:','pop rax','ret'];header += ['extern \"C\" uint64_t hw_getpc();','extern \"C\" Memory* sub_100092000(State*,uint64_t,Memory*);']
(out/'call-entries.h').write_text('\n'.join(header)+'\n',encoding='utf-8');(out/'authored.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');write_json(out/'specs.json',specs)
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
blob=(out/'authored.obj').read_bytes();machine,sections=struct.unpack_from('<HH',blob);assert machine==0x8664;opt=struct.unpack_from('<H',blob,16)[0];text=None
for n in range(sections):
 at=20+opt+40*n
 if blob[at:at+8].rstrip(b'\0')==b'.text':
  size,pointer=struct.unpack_from('<II',blob,at+16);text=blob[pointer:pointer+size]
assert text is not None;decoder=Cs(CS_ARCH_X86,CS_MODE_64);rows=[];roots=[];contracts=[]
for n,s in enumerate(specs):
 for offset,count in [(0,3),(32,2),(64,2 if s['mode']==1 else 1)]:
  ins=list(decoder.disasm(text[n*256+offset:n*256+offset+24],s['pc']+offset,count=count));assert len(ins)==count and ins[-1].mnemonic=='ret';rows += [dict(address=i.address,bytes=i.bytes.hex()) for i in ins]
 roots += [s['pc'],s['pc']+s['length'],s['pc']+32,s['pc']+64]
 if s['mode']==2:contracts.append(dict(address=s['pc'],expected_next_pc=s['pc']+s['length'],kind='no-normal-return',provenance='authored fixture asserts a conditional nonreturn contract; no runtime implementation is inferred'))
if not a.expect_unchecked:
 roots.append(0x100092000);rows += [dict(address=0x100092000+offset,bytes=code) for offset,code in [(0,'e800000000'),(5,'58'),(6,'c3')]]
write_json(out/'input.json',dict(roots=roots,instructions=rows,return_contracts=contracts))
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()])
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64',*(['/DBB_INCLUDE_GETPC=1'] if not a.expect_unchecked else []),'/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/sparse_lift/call_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe','unchecked' if a.expect_unchecked else 'checked']);result=json.loads((out/'execute.stdout').read_text(encoding='utf-8'));assert result['status']=='pass'
write_json(out/'summary.json',dict(status='legacy unchecked call-return behavior reproduced' if a.expect_unchecked else 'authored source-aware call-return checks pass',result=result,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),input_sha256=sha(out/'input.json'),bitcode_sha256=sha(out/'function.bc'),object_sha256=sha(out/'function.obj'),fixture_sha256=sha(out/'fixture.exe'),raw_sha256=sha(out/'execute.stdout'),limitations='Authored static hardware and AOT only. The nonreturn assertion is a fixture contract; tests do not implement native nonlocal transfer or game startup.'))
print(json.dumps(result),flush=True)
