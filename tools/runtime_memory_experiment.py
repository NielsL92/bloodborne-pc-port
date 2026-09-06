"""Build native registered-memory support and exercise bounded RAM contracts."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
def run(name,argv,expected=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==expected,(name,r.returncode)
objects=[]
for name in ['fault','memory','memory_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text(encoding='utf-8'));assert positive['status']=='pass';negative=[]
for mode,reason,boundary in [('read-unmapped',4,'memory-read'),('overflow',4,'memory-read'),('write-ro',4,'memory-write'),('cross-permission',4,'memory-write'),('code-write',7,'code-write-uncovered'),('alignment',3,'memory-alignment'),('nested-atomic',5,'nested-atomic'),('unpaired-atomic',6,'unpaired-atomic'),('unsealed',2,'unsealed-memory'),('wrong-state',1,'context'),('wrong-thread',1,'context')]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);record=json.loads((out/(mode+'.stderr')).read_text(encoding='utf-8'));assert record['boundary']==boundary and record['reason']==reason and record['pc']=='0000000123456789';negative.append(dict(mode=mode,boundary=boundary,reason=reason))
for mode in ['overlap','writable-code']:run(mode,[out/'fixture.exe',mode]);assert json.loads((out/(mode+'.stdout')).read_text())['status']=='setup-rejected'
summary=dict(status='native private RAM boundary checks pass',positive=positive,negative=negative,setup_rejections=2,source_sha256={str(p):sha(p) for p in sorted((ROOT/'native/runtime').glob('*')) if p.is_file()},limitations='Native runtime unit checks only, with private NX mappings and serialized registered accesses. No AOT/game execution, arbitrary external writers, MMIO, guest exception recovery, performance claim or general console memory-model proof.');write_json(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],positive=positive,negative_cases=len(negative),setup_rejections=2)),flush=True)
