"""Validate main static TLS initialization and explicit State FS addressing."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x100500000
body=[]
for index,code in enumerate([['64488b042500000000','4801f8','488930','488b00','c3'],['64488b042500000000','4801f8','488b00','c3'],['64488b042500000000','c3']]):
 at=pc+256*index
 for raw in code:body.append(dict(address=at,bytes=raw));at+=len(bytes.fromhex(raw))
write_json(out/'input.json',dict(native_memory_provenance=True,roots=[pc+i*256 for i in range(3)],instructions=body))
header=[f'extern "C" Memory* sub_{pc+i*256:x}(State*,uint64_t,Memory*);' for i in range(3)];header.append('#define TLS_TARGETS {'+','.join('{'+str(pc+i*256)+'ULL,sub_'+format(pc+i*256,'x')+'}' for i in range(3))+'}');(out/'tls-entries.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')

def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
lifter=ROOT/'build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe';semantics=ROOT/'build/extended-semantics-v35-divide';run('lift',[lifter,out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',semantics]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','main_tls','main_tls_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['aot_calls']==3752 and positive['native_threads']==8
for mode,reason in [('missing',4),('guard',8),('lower',4)]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);fault=json.loads((out/(mode+'.stderr')).read_text().splitlines()[0]);assert fault['reason']==reason and int(fault['source'],16)==pc+(512 if mode=='missing' else 256+12)
run('duplicate',[out/'fixture.exe','duplicate'])
result=dict(status='native main TLS initialization and AOT FS checks pass',positive=positive,negative_stops=3,duplicate_initialization_rejected=True,objects={p.name:sha(p) for p in objects},lifter_sha256=sha(lifter),semantics_sha256=sha(semantics/'amd64_avx.bc'),game_aot_execution=False,limits=['Authored native thread contexts test explicit State FS bases, independent templates and zero fill. Host FS is never changed.','Only main initial-exec storage and the TCB self pointer are provided. Other TCB fields remain guarded; module/DTV references are unresolved.']);write_json(out/'summary.json',result);print(json.dumps(result),flush=True)
