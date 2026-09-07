"""Validate native direct-memory allocation, mapping aliases and AOT service ABI."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x100300000
# Indirect calls carry canonical logical service identifiers; no 32-bit displacement assumption.
body=[]
for i,target in enumerate([0x900002000+i*16 for i in range(4)]):
 at=pc+0x100*i;body.extend([dict(address=at,bytes='48b8'+target.to_bytes(8,'little').hex()),dict(address=at+10,bytes='ffd0'),dict(address=at+12,bytes='c3')])
write_json(out/'input.json',dict(native_memory_provenance=True,roots=[pc+i*0x100 for i in range(4)],instructions=body))
header=[f'extern \"C\" Memory* sub_{pc+i*256:x}(State*,uint64_t,Memory*);' for i in range(4)];header.append('#define DIRECT_TARGETS {'+','.join('{'+str(pc+i*256)+'ULL,sub_'+format(pc+i*256,'x')+'}' for i in range(4))+'}');(out/'direct-entries.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')
def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
lifter=ROOT/'build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe';semantics=ROOT/'build/extended-semantics-v35-divide';run('lift',[lifter,out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',semantics]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','direct_memory','direct_memory_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['allocation_release_pairs']==2048 and positive['alias_pairs']==64 and positive['size_query_above_4g']
for mode,reason in [('missing-provider',70),('bad-output',4),('memory-type',64),('map-mode',65),('partial-release',67),('mapped-release',68),('map-hint',66),('map-bounds',4),('old-guard',8),('old-code',7)]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);fault=json.loads((out/(mode+'.stderr')).read_text().splitlines()[0]);assert fault['reason']==reason
result=dict(status='native direct-memory allocation mapping and AOT checks pass',positive=positive,negative_stops=10,objects={p.name:sha(p) for p in objects},lifter_sha256=sha(lifter),semantics_sha256=sha(semantics/'amd64_avx.bc'),game_aot_execution=False,limits=["Native bounded memory-type-zero allocations, zero-hint RW maps and exact unmapped release only. GPU modes, other map flags, unmapping and partial/mapped release remain unimplemented.",'Authored allocation and mapping checks only; no game gateway is bound by this fixture.','Guest CPU pointers address registered NX mappings; direct physical offsets identify native backing allocations.','Live-resource and monotonically increasing identifier bounds are native implementation limits, not console resource limits.']);write_json(out/'summary.json',result);print(json.dumps(result),flush=True)
