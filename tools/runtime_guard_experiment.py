"""Exercise unresolved relocation guards in native helpers and authored AOT."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x1000e0000
body=[(0,'90'),(1,'488b07'),(4,'c3'),(16,'90'),(17,'488907'),(20,'c3'),(0x100,'85c9'),(0x102,'7406'),(0x104,'90'),(0x105,'488b07'),(0x108,'eb04'),(0x10a,'90'),(0x10b,'488b07'),(0x10e,'c3'),(0x200,'b903000000'),(0x205,'90'),(0x206,'4883c701'),(0x20a,'ffc9'),(0x20c,'75f7'),(0x20e,'488b07'),(0x211,'c3'),(0x300,'90'),(0x301,'e83a000000'),(0x306,'90'),(0x307,'488b07'),(0x30a,'c3'),(0x340,'90'),(0x341,'488b06'),(0x344,'c3'),(0x400,'90'),(0x401,'0fae07'),(0x404,'c3')]
roots=[pc+x for x in [0,16,0x100,0x200,0x300,0x340,0x400]]
write_json(out/'input.json',dict(native_memory_provenance=True,roots=roots,instructions=[dict(address=pc+offset,bytes=code) for offset,code in body]))
header=[f'extern "C" Memory* sub_{at:x}(State*,uint64_t,Memory*);' for at in roots]
header+=['static const bb_runtime::Target roots[]={'+','.join('{'+f'{at}ULL,sub_{at:x}'+'}' for at in roots)+'};']
(out/'guard-entries.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')
def run(name,argv,expected=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==expected,(name,r.returncode)
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','guard_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['aot_cases']==2568 and positive['guards']==2
negative=[]
for mode in ['read','write','cas','atomic-read','aot-read','aot-write']:
 cases=[(offset,width) for offset in range(120,140) for width in ([1,2,4,8,16] if mode in ['read','write'] else [8]) if offset<136 and 128<offset+width]+[(4088,8),(4092,8),(4096,8)]
 for offset,width in cases:
  name=f'{mode}-{offset}-{width}';run(name,[out/'fixture.exe',mode,offset,width],0xb0000008);records=[json.loads(line) for line in (out/(name+'.stderr')).read_text().splitlines()];fault,guard=records;assert fault['boundary']=='unresolved-relocation' and guard['completed_memory_operations']==0;source=pc+(17 if mode=='aot-write' else 1 if mode=='aot-read' else 0);assert int(fault['source'],16)==source and int(fault['address'],16)==0x70000000+offset and fault['width']==width
  assert guard['unresolved_identity']==('authored-slot-A' if offset<4000 else 'authored-cross-region');assert guard['guard_size']==8;negative.append(dict(mode=mode,offset=offset,width=width,source=source))
for mode,source,operations,width in [('flow-branch-zero',0x10b,0,8),('flow-branch-nonzero',0x105,0,8),('flow-loop',0x20e,0,8),('flow-inner',0x341,1,8),('flow-outer',0x307,3,8),('flow-span',0x401,0,512)]:
 run(mode,[out/'fixture.exe',mode],0xb0000008);records=[json.loads(line) for line in (out/(mode+'.stderr')).read_text().splitlines()];fault,guard=records[:2];assert int(fault['source'],16)==int(fault['pc'],16)==pc+source,(mode,fault);assert fault['width']==width and guard['completed_memory_operations']==operations,(mode,records);assert guard['unresolved_identity']=='authored-slot-A';negative.append(dict(mode=mode,source=pc+source,completed_memory_operations=operations,width=width))
for mode in ['setup-overlap','setup-zero','setup-unmapped','setup-sealed']:run(mode,[out/'fixture.exe',mode]);assert json.loads((out/(mode+'.stdout')).read_text())['status']=='setup-rejected'
summary=dict(status='native unresolved-slot guard checks pass',positive=positive,negative=negative,setup_rejections=4,source_sha256={str(p):sha(p) for p in sorted((ROOT/'native/runtime').glob('*')) if p.is_file()},limitations='Authored data/AOT only. Guards stop before exposing unresolved slots; these checks do not resolve symbols, load game modules or execute game CPU code.');write_json(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],positive=positive,negative_cases=len(negative))),flush=True)
