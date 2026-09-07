"""Validate real native mutex-attribute state through authored AOT call/return boundaries."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x100100000
# Indirect calls carry canonical logical service identifiers; no 32-bit displacement assumption.
body=[]
for i,target in enumerate([0x900000100,0x900000110,0x900000120]):
 at=pc+0x100*i;body.extend([dict(address=at,bytes='48b8'+target.to_bytes(8,'little').hex()),dict(address=at+10,bytes='ffd0'),dict(address=at+12,bytes='c3')])
write_json(out/'input.json',dict(native_memory_provenance=True,roots=[pc+i*0x100 for i in range(3)],instructions=body))
def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
lifter=ROOT/'build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe';semantics=ROOT/'build/extended-semantics-v35-divide';run('lift',[lifter,out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',semantics]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','mutexattr','mutexattr_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['lifecycles']==4096 and positive['aot_service_calls']==45059
for mode,reason in [('bad-pointer',4),('missing-provider',54),('double-init',53),('opaque-read',4)]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);fault=json.loads((out/(mode+'.stderr')).read_text().splitlines()[0]);assert fault['reason']==reason
result=dict(status='native mutex attribute lifecycle and AOT service ABI checks pass',positive=positive,negative_stops=4,objects={p.name:sha(p) for p in objects},lifter_sha256=sha(lifter),semantics_sha256=sha(semantics/'amd64_avx.bc'),game_aot_execution=False,limits=['Authored stateful service checks only; no game gateway is bound by this fixture.','Opaque logical identifiers are not host pointers or guest-readable attribute layouts. Direct dereference remains an explicit unsupported memory stop.','Live-resource and monotonically increasing identifier bounds are native implementation limits, not console resource limits.']);write_json(out/'summary.json',result);print(json.dumps(result),flush=True)
