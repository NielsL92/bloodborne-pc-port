"""Build a read-only Remill decoder inspector from the pinned configured libraries."""
import re,subprocess,sys
from pathlib import Path
from tools.build_sparse_lift import arguments
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);text=(ROOT/'build/remill/build.ninja').read_text(encoding='utf-8')
def block(prefix):
 matches=[m.group(0) for m in re.finditer(r'^build [^\n]+\n(?:  [^\n]*\n)*',text,re.M) if m.group(0).startswith(prefix)];assert len(matches)==1;return matches[0]
def field(block,name):return re.search(r'^  '+name+r' = (.*)$',block,re.M).group(1)
compile=block('build bin/lift/CMakeFiles/remill-lift-21.dir/Lift.cpp.obj:');link=block('build bin/lift/remill-lift-21.exe:')
flags=arguments(' '.join(field(compile,key) for key in ('DEFINES','FLAGS','INCLUDES')));libs=arguments(field(link,'LINK_LIBRARIES'));identities={}
for n,lib in enumerate(libs):
 p=Path(lib)
 if not p.is_absolute() and (ROOT/'build/remill'/p).is_file():p=ROOT/'build/remill'/p
 if p.is_absolute() and p.is_file():libs[n]=str(p);identities[str(p)]=sha(p)
source=ROOT/'native/sparse_lift/inspect.cpp';env=environment();steps=[]
for name,argv in [('compile',[LLVM/'bin/clang-cl.exe',*flags,'/c',source,'/Fo'+str(out/'inspect.obj')]),('link',[LLVM/'bin/lld-link.exe',out/'inspect.obj',*libs,'/machine:x64','/subsystem:console','/threads:2','/out:'+str(out/'inspect.exe')])]:
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=300)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0
write_json(out/'identity.json',dict(source_sha256=sha(source),executable_sha256=sha(out/'inspect.exe'),compiler_sha256=sha(LLVM/'bin/clang-cl.exe'),linked_library_sha256=identities,semantics_sha256=sha(ROOT/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc'),execution='none'))
print('Read-only decoder inspector built',flush=True)
