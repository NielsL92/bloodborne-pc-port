"""Build an isolated manifest lifter from pinned Remill libraries, without rebuilding them."""
import ctypes
import json
from pathlib import Path
import re
import subprocess
import sys
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM,ROOT,environment

def arguments(text):
    """Parse generated Windows compiler arguments; never execute command text."""
    count=ctypes.c_int();parse=ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)]
    parse.restype=ctypes.POINTER(ctypes.c_wchar_p)
    result=parse('program '+text,ctypes.byref(count))
    try:return [result[i] for i in range(1,count.value)]
    finally:ctypes.windll.kernel32.LocalFree(ctypes.cast(result,ctypes.c_void_p))

def main():
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'external/remill/lib/BC/TraceLifter.cpp'
    assert sha(source)=='edc99939625213dcf0a3312da1fde8d0824a4e3544faaf93d33dec42b347623a'
    text=source.read_text(encoding='utf-8')
    replacements=[
      ('namespace remill {','extern bool bb_sparse_instruction_start(uint64_t);\nextern void bb_sparse_instruction_decoded(uint64_t,const remill::Instruction&);\nextern void bb_sparse_instruction_lifted(uint64_t,int);\n\nnamespace remill {'),
      ('bool TraceLifter::Impl::ReadInstructionBytes(uint64_t addr) {','bool TraceLifter::Impl::ReadInstructionBytes(uint64_t addr) {\n  if (!bb_sparse_instruction_start(addr)) return false;'),
      ('auto lift_status =\n          inst.GetLifter()->LiftIntoBlock(inst, block, state_ptr);','bb_sparse_instruction_decoded(inst_addr,inst);\n      auto lift_status =\n          inst.GetLifter()->LiftIntoBlock(inst, block, state_ptr);'),
      ('if (kLiftedInstruction != lift_status) {\n        AddTerminatingTailCall(block, intrinsics->error, *intrinsics);','bb_sparse_instruction_lifted(inst_addr,static_cast<int>(lift_status));\n      if (kLiftedInstruction != lift_status) {\n        AddTerminatingTailCall(block, intrinsics->error, *intrinsics);')]
    for old,new in replacements:
        assert text.count(old)==1,old;text=text.replace(old,new)
    trace=out/'TraceLifter-audited.cpp';trace.write_text(text,encoding='utf-8')
    ninja=ROOT/'build/remill/build.ninja';description=ninja.read_text(encoding='utf-8')
    def block(prefix):
        matches=[m.group(0) for m in re.finditer(r'^build [^\n]+\n(?:  [^\n]*\n)*',description,re.M) if m.group(0).startswith(prefix)]
        assert len(matches)==1,prefix;return matches[0]
    compile_block=block('build bin/lift/CMakeFiles/remill-lift-21.dir/Lift.cpp.obj:')
    link_block=block('build bin/lift/remill-lift-21.exe:')
    def field(block,name):return re.search(r'^  '+name+r' = (.*)$',block,re.M).group(1)
    flags=arguments(' '.join(field(compile_block,k) for k in ('DEFINES','FLAGS','INCLUDES')))
    flags.append('/I'+str(ROOT/'external/remill/lib/BC'))
    libs=arguments(field(link_block,'LINK_LIBRARIES'));identities={}
    for n,item in enumerate(libs):
        candidate=Path(item)
        if not candidate.is_absolute() and (ROOT/'build/remill'/candidate).is_file():candidate=ROOT/'build/remill'/candidate
        if candidate.is_absolute() and candidate.is_file():libs[n]=str(candidate);identities[str(candidate)]=sha(candidate)
    env=environment();steps=[];objects=[]
    def run(argv,name):
        with (out/(name+'.stdout.log')).open('wb') as stdout,(out/(name+'.stderr.log')).open('wb') as stderr:
            r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=300)
        steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps)
        if r.returncode:raise RuntimeError(f'{name} failed; see {out}')
    for name,path in (('driver',ROOT/'native/sparse_lift/main.cpp'),('trace',trace)):
        obj=out/(name+'.obj');objects.append(obj)
        run([LLVM/'bin/clang-cl.exe',*flags,'/c',path,'/Fo'+str(obj)],name)
    exe=out/'bb-sparse-lift.exe'
    run([LLVM/'bin/lld-link.exe',*objects,*libs,'/machine:x64','/subsystem:console','/threads:2','/out:'+str(exe)],'link')
    write_json(out/'identity.json',dict(status='isolated sparse driver built',driver_source_sha256=sha(ROOT/'native/sparse_lift/main.cpp'),
        original_trace_source_sha256=sha(source),audited_trace_sha256=sha(trace),build_ninja_sha256=sha(ninja),
        compiler_sha256=sha(LLVM/'bin/clang-cl.exe'),linker_sha256=sha(LLVM/'bin/lld-link.exe'),
        linked_library_sha256=identities,executable_sha256=sha(exe),
        scope='Adds entry and post-decode audit hooks to a local copy of pinned TraceLifter.cpp. Existing Remill executable and libraries untouched. No input-code execution.'))
    print(json.dumps(dict(status='pass',executable=str(exe),sha256=sha(exe))),flush=True)

if __name__=='__main__':main()
