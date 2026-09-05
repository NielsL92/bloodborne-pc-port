"""Build an isolated semantic module from the pinned recipe plus authored extensions."""
import re,subprocess,sys
from pathlib import Path
from tools.build_sparse_lift import arguments
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
text=(ROOT/'build/remill/build.ninja').read_text(encoding='utf-8')
blocks=[m.group(0) for m in re.finditer(r'^build [^\n]+\n(?:  [^\n]*\n)*',text,re.M) if m.group(0).startswith('build lib/Arch/X86/Runtime/amd64_avx_Instructions.cpp.bc ')]
assert len(blocks)==1
command=re.search(r'^  COMMAND = (.*)$',blocks[0],re.M).group(1);tail=command.split('&& ',1)[1];assert tail.endswith('"');argv=arguments(tail[:-1]);assert Path(argv[0]).resolve()==(LLVM/'bin/clang++.exe').resolve()
original=ROOT/'external/remill/lib/Arch/X86/Runtime/Instructions.cpp';extension=ROOT/'native/semantics/BMI.cpp.inc'
unit=out/'Instructions-extended.cpp';unit.write_text(f'#include "{original.as_posix()}"\n#include "{extension.as_posix()}"\n',encoding='utf-8')
assert Path(argv[argv.index('-c')+1]).resolve()==original.resolve();argv[argv.index('-c')+1]=str(unit);argv[argv.index('-o')+1]=str(out/'instructions.bc')
inputs=[ROOT/'build/remill/lib/Arch/X86/Runtime'/('amd64_avx_'+n+'.cpp.bc') for n in ('BasicBlock','Intrinsics','HyperCall')];env=environment();steps=[]
for name,cmd in [('compile',argv),('link',[LLVM/'bin/llvm-link.exe','--suppress-warnings',out/'instructions.bc',*inputs,'-o',out/'amd64_avx.bc'])]:
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,cmd)),env=env,stdout=stdout,stderr=stderr,timeout=300)
 steps.append(dict(argv=list(map(str,cmd)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0
original_inputs={p.relative_to(ROOT).as_posix():sha(p) for directory in ('external/remill/include/remill','external/remill/lib/Arch/X86') for p in sorted((ROOT/directory).rglob('*')) if p.is_file()}
write_json(out/'identity.json',dict(status='isolated semantic module built',extension_sha256=sha(extension),original_source_sha256=original_inputs,linked_bitcode_sha256={str(p):sha(p) for p in inputs},original_semantics_sha256=sha(ROOT/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc'),semantics_sha256=sha(out/'amd64_avx.bc'),compiler_sha256=sha(LLVM/'bin/clang++.exe'),execution='none; semantics require independent authored checks'))
print('Isolated extended semantic module built',flush=True)
