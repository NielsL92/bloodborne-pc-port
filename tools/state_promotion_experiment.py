"""Apply the bounded state promotion experiment and validate existing full-state contracts."""
import argparse,hashlib,json,subprocess,sys,time,shutil,statistics
from pathlib import Path
from tools.dev import environment,LLVM
p=argparse.ArgumentParser();p.add_argument("out");p.add_argument("--measure",action="store_true");a=p.parse_args()
root=Path.cwd();out=root/a.out;env=environment()
def run(cmd,log):
    start=time.perf_counter()
    with (out/(log+".stdout")).open("wb") as o,(out/(log+".stderr")).open("wb") as e:
        r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=180)
    print(json.dumps(dict(step=log,exit=r.returncode,seconds=time.perf_counter()-start)),flush=True)
    if r.returncode: raise RuntimeError(f"{log} failed; see preserved stdout/stderr")
def save(path,data):path.write_bytes((json.dumps(data,indent=2)+"\n").encode("utf-8"))
initial=root/"local/compiler-spike/initial";graphs=root/"local/compiler-spike/graphs-return-count";simd=root/"local/compiler-spike/varied-cmpss-fixed"
clang=LLVM/"bin/clang.exe";cxx=LLVM/"bin/clang-cl.exe";opt=LLVM/"bin/opt.exe"
graph_names=["2550","65d0","b820","2fa30","3df50","3240","5e4e0","77e80","2b2b0"]
if not a.measure:
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(root/"build/state-promotion/bb-state-promotion.exe",out/"promotion.exe")
    cases={"3360":initial,**{x:graphs/x for x in graph_names},**{x:simd/x for x in ["1a50","3500","3530"]}}
    for rva,src in cases.items():
        folder=out/rva;folder.mkdir()
        run([sys.executable,"tools/lower_intrinsics.py",src/"function.ll",folder/"lowered.ll"],rva+"-lower")
        run([opt,"-S","-passes=default<O2>",folder/"lowered.ll","-o",folder/"canonical.ll"],rva+"-canonical")
        run([out/"promotion.exe",folder/"canonical.ll",folder/"promoted.ll"],rva+"-promote")
        run([opt,"-S","-passes=default<O2>",folder/"promoted.ll","-o",folder/"optimized.ll"],rva+"-optimize")
        run([clang,"-c","-O2","-march=haswell",folder/"optimized.ll","-o",folder/"function.obj"],rva+"-object")
        run([LLVM/"bin/llvm-objdump.exe","-d","--x86-asm-syntax=intel",folder/"function.obj"],rva+"-asm")
    run([clang,"-c","-march=haswell","native/remill_oracle.S","-o",out/"oracle.obj"],"oracle")
    common=[cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include"]
    groups={"loop_test":["3360"],"varied_test":["1a50","3500","3530"],"graph_test":graph_names,"benchmark":["3360"],"hash_benchmark":graph_names}
    for name,funcs in groups.items():
        run([*common,f"native/remill_{name}.cpp",f"/Fo{out}/{name}.obj"],name+"-compile")
        run([cxx,"/nologo",out/(name+".obj"),out/"oracle.obj",*[out/x/"function.obj" for x in funcs],f"/Fe{out}/{name}.exe"],name+"-link")
    tests=[("3360",[out/"loop_test.exe",initial/"original.bin"])]
    tests += [(x,[out/"varied_test.exe",simd/x/"original.bin",x]) for x in ["1a50","3500","3530"]]
    tests += [(x,[out/"graph_test.exe",graphs,x]) for x in graph_names[:6]]
    results=[]
    for rva,cmd in tests:
        run(cmd,rva+"-test")
        result=json.loads((out/(rva+"-test.stdout")).read_text().splitlines()[-1]);results.append(result)
    save(out/"correctness.json",results)
    save(out/"artifacts.json",{str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob("*") if f.is_file()})
else:
    if not (out/"correctness.json").exists():raise RuntimeError("validate before timing")
    measure=out/"measurement";measure.mkdir(exist_ok=False)
    summary=[]
    for label,name,src in [("loop","benchmark",initial/"original.bin"),("hash","hash_benchmark",graphs)]:
        run([out/(name+".exe"),src],label+"-timing")
        rows=[json.loads(x) for x in (out/(label+"-timing.stdout")).read_text().splitlines()]
        for length in sorted({x["length"] for x in rows}):
            values=[x for x in rows if x["length"]==length]
            summary.append(dict(kernel=label,length=length,repetitions=len(values),median_ratio=statistics.median(x["ratio"] for x in values),median_native_ns=statistics.median(x["native_ns"] for x in values),median_aot_ns=statistics.median(x["aot_ns"] for x in values)))
    save(measure/"summary.json",summary);print(json.dumps(summary),flush=True)
