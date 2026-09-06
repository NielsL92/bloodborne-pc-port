"""Exercise explicit FP profiles and numeric bindings through authored AOT only."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('library',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x1000d0000
forms=[('dd1f','DS'),('dd5d00','SS'),('26dd1f','ES'),('2edd1f','CS'),('3edd1f','DS'),('64dd1f','FS'),('65dd1f','GS')]
roots=[];rows=[];sites=[]
def body(offset,items):
 at=pc+offset;roots.append(at)
 for code,segment in items:
  rows.append(dict(address=at,bytes=code))
  if segment is not None:
   data=bytes.fromhex(code);i=next(i for i,v in enumerate(data) if 0xd8<=v<=0xdf);sites.append(dict(pc=at,fop=((data[i]&7)<<8)|data[i+1],segment=segment))
  at+=len(code)//2
for i,(store,seg) in enumerate(forms):body(i*64,[('dbe3',None),('d9e8','None'),(store,seg),('c3',None)])
body(0x200,[('dd07','DS'),('d9e8','None'),('dec1','None'),('dd1e','DS'),('c3',None)])
for offset,code in [(0x300,'0fae17'),(0x340,'48f7f1'),(0x380,'0f2fc1'),(0x3c0,'9b'),(0x440,'0fae07')]:body(offset,[(code,None),('c3',None)])
body(0x400,[('d9e8','None'),('d9e8','None'),('dec1','None'),('c3',None)])
roots.sort();sites.sort(key=lambda s:s['pc']);write_json(out/'input.json',dict(native_memory_provenance=True,roots=roots,instructions=rows));write_json(out/'sites.json',sites)
header=[f'extern "C" Memory* sub_{at:x}(State*,uint64_t,Memory*);' for at in roots]
header+=['static const bb_runtime::Target targets[]={'+','.join('{'+f'{at}ULL,sub_{at:x}'+'}' for at in roots)+'};']
header+=['static const bb_runtime::X87Site sites[]={'+','.join('{'+f"{s['pc']}ULL,{s['fop']},bb_runtime::Segment::{s['segment']}"+'}' for s in sites)+'};']
(out/'runtime-fp-entries.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')
def run(name,argv,expected=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==expected,(name,r.returncode)
run('lift',[a.lifter.resolve(),out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',a.semantics.resolve()]);run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',out/'function.bc','-o',out/'function.obj']);objects=[out/'function.obj']
for name in ['fault','memory','control','intrinsics','fp','sourced','fp_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('numeric',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/c',ROOT/'native/semantics/x87_numeric.cpp','/Fo'+str(out/'numeric.obj')]);objects.append(out/'numeric.obj');builtins=LLVM/'lib/clang/21/lib/windows/clang_rt.builtins-x86_64.lib'
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,a.library.resolve(),builtins,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['aot_cases']==32768
negative=[]
for mode,reason,boundary,source in [('no-profile',40,'unconfigured-fp-profile',None),('unknown-site',41,'unknown-x87-site',pc+0x200),('bad-site-fop',41,'x87-metadata-contract',pc+0x200),('span-write',42,'x87-span-contract',pc),('span-unmapped',4,'memory-read',pc),('image-alignment',3,'memory-alignment',pc+0x440),('divide-zero',43,'integer-divide',pc+0x340),('divide-overflow',43,'integer-divide',pc+0x340),('mxcsr',44,'mxcsr-reserved-bits',pc+0x300),('simd',45,'simd-unmasked',pc+0x380),('x87-pending',46,'x87-pending',pc+0x3c0),('x87-unsupported',47,'x87-unsupported',pc+0x404)]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);records=[json.loads(line) for line in (out/(mode+'.stderr')).read_text().splitlines()];r=records[0];assert r['reason']==reason and r['boundary']==boundary,(mode,r)
 if source is not None:assert int(r['source'],16)==source,(mode,r)
 if mode!='no-profile':assert records[1]['fp_profile']=='authored-explicit-profile'
 if mode.startswith('divide-'):assert int(r['actual'],16)==(1 if mode=='divide-zero' else 2) and r['width']==64
 if mode=='mxcsr':assert int(r['actual'],16)==0x80001f80 and int(r['wanted'],16)==0x80000000 and records[1]['mxcsr']==0x1f80
 if mode=='simd':assert int(r['actual'],16)==int(r['wanted'],16)==1 and records[1]['mxcsr']==0x1f01
 if mode=='x87-pending':assert int(r['actual'],16)==1 and records[1]['x87_status']==0x8081
 if mode=='x87-unsupported':assert int(r['actual'],16)==1 and records[1]['x87_control']==0x17f

 negative.append(dict(mode=mode,reason=reason,boundary=boundary,source=source))
for mode in ['bad-policy','bad-mask','duplicate-sites']:run(mode,[out/'fixture.exe',mode]);assert json.loads((out/(mode+'.stdout')).read_text())['status']=='setup-rejected'
summary=dict(status='authored AOT FP runtime profile/numeric boundaries pass',positive=positive,negative=negative,setup_rejections=3,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),softfloat_sha256=sha(a.library),builtins_sha256=sha(builtins),source_sha256={str(p):sha(p) for p in sorted((ROOT/'native/runtime').glob('*')) if p.is_file()},limitations='Explicit authored profiles only. No inferred PS4 profile, guest exception recovery, game execution or game service implementation.');write_json(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],positive=positive,negative_cases=len(negative))),flush=True)
