"""Compile the fixed SoftFloat 3e recipe as a Windows native static library."""
import argparse,concurrent.futures,json,re,subprocess,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);source=ROOT/'external/SoftFloat-3e';env=environment()
record=json.loads((ROOT/'reports/softfloat-source.json').read_text(encoding='utf-8'))
for name,digest in record['files'].items():assert sha(source/name)==digest
make=(source/'build/Linux-x86_64-GCC/Makefile').read_text(encoding='utf-8');sources=[]
for key,subdir in [('OBJS_PRIMITIVES',''),('OBJS_SPECIALIZE','8086'),('OBJS_OTHERS','')]:
 block=re.search(r'^'+key+r' = \\\n(.*?)(?=\n\n)',make,re.M|re.S).group(1)
 for name in re.findall(r'(\w+)\$\(OBJ\)',block):
  src=source/'source'/subdir/(name+'.c');assert src.is_file();sources.append(src)
assert len(sources)==len({s.name for s in sources})
# Preserve the upstream GNU/Clang integer primitive configuration; only TLS
# storage is supplied as a build definition, without editing upstream files.
(out/'platform.h').write_bytes((source/'build/Linux-x86_64-GCC/platform.h').read_bytes())
def compile_one(src):
 target=out/(src.stem+'.obj');argv=[LLVM/'bin/clang.exe','-c','-std=c11','-O2','-mno-incremental-linker-compatible','-Werror=implicit-function-declaration','-DSOFTFLOAT_FAST_INT64','-DSOFTFLOAT_ROUND_ODD','-DINLINE_LEVEL=5','-DSOFTFLOAT_FAST_DIV32TO16','-DSOFTFLOAT_FAST_DIV64TO32','-DTHREAD_LOCAL=_Thread_local','-I'+str(out),'-I'+str(source/'source/8086'),'-I'+str(source/'source/include'),src,'-o',target]
 with (out/(src.stem+'.stdout')).open('wb') as stdout,(out/(src.stem+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=60)
 return dict(source=src.relative_to(ROOT).as_posix(),source_sha256=sha(src),argv=list(map(str,argv)),exit_code=r.returncode,object_sha256=sha(target) if target.exists() else None)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:steps=list(pool.map(compile_one,sources))
write_json(out/'compile-steps.json',steps);assert all(r['exit_code']==0 for r in steps),'source compilation failure; inspect per-file logs'
argv=[LLVM/'bin/llvm-ar.exe','rcsD',out/'softfloat.lib',*[out/(s.stem+'.obj') for s in sources]]
with (out/'archive.stdout').open('wb') as stdout,(out/'archive.stderr').open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=60)
assert r.returncode==0
summary=dict(status='SoftFloat native Windows library built; numeric correctness not yet evaluated',source_archive_sha256=record['sha256'],specialization='8086',thread_local=True,objects=len(sources),library_sha256=sha(out/'softfloat.lib'),compiler_sha256=sha(LLVM/'bin/clang.exe'),platform_sha256=sha(out/'platform.h'),archive_argv=list(map(str,argv)),source_mutations=False)
write_json(out/'identity.json',summary);print(json.dumps(summary),flush=True)
