"""Validate opaque native canary storage and authored AOT mismatch handling."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x1000f0000
body=[(0,'55'),(1,'4889e5'),(4,'4883ec10'),(8,'488b07'),(11,'488945f8'),(15,'4889f0'),(18,'483117'),(21,'488b0f'),(24,'48394df8'),(28,'7506'),(30,'4883c410'),(34,'5d'),(35,'c3'),(36,'e8d70f0000')]
write_json(out/'input.json',dict(native_memory_provenance=True,roots=[pc],instructions=[dict(address=pc+at,bytes=code) for at,code in body],return_contracts=[dict(address=pc+36,expected_next_pc=pc+41,kind='no-normal-return',provenance='authored canary mismatch must stop at the unimplemented failure gateway')]))
def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
lifter=ROOT/'build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe';semantics=ROOT/'build/extended-semantics-v35-divide';run('lift',[lifter,out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',semantics]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','canary','canary_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['aot_cases']==4096
for bit in range(64):
 name=f'bit-{bit:02d}';run(name,[out/'fixture.exe','negative',bit],0xb0000019);fault,active=[json.loads(s) for s in (out/(name+'.stderr')).read_text().splitlines()];assert fault['boundary']=='unimplemented-import' and int(fault['pc'],16)==pc+0x1000 and active['nid']=='Ou3iL1abvng'
for mode in ['wide','offset']:run(mode,[out/'fixture.exe',mode],0xb0000004);assert json.loads((out/(mode+'.stderr')).read_text())['boundary']=='memory-read'
run('double-init',[out/'fixture.exe','double-init']);assert json.loads((out/'double-init.stdout').read_text())['status']=='setup-rejected';run('entropy',[out/'fixture.exe','entropy']);assert json.loads((out/'entropy.stdout').read_text())['bytes']==8
result=dict(status='native canary storage and authored AOT mismatch checks pass',positive=positive,mismatch_bits=64,out_of_bounds_stops=2,reinitialization_rejections=1,native_entropy_bytes=8,lifter_sha256=sha(lifter),semantics_sha256=sha(semantics/'amd64_avx.bc'),objects={p.name:sha(p) for p in objects},source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native/runtime').glob('*') if p.is_file()},game_execution=False,limits='Authored canary use only. Recorded seed injection is explicit; native entropy acquisition has no constant fallback. A mismatch reaches the explicit unimplemented failure gateway. No game data binding or guard removal is performed.');write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],positive=positive,mismatch_bits=64)),flush=True)
