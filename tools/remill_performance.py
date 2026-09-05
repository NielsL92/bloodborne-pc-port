"""Build, validate, then separately time helper and contract-lowered AOT."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from tools.dev import environment,LLVM
p=argparse.ArgumentParser();p.add_argument("--run-only",action="store_true");a=p.parse_args()
root=Path.cwd();out=root/"local/compiler-spike/performance";env=environment();clang=str(LLVM/"bin/clang.exe");cxx=str(LLVM/"bin/clang-cl.exe")
def run(cmd):
 print(json.dumps(cmd),flush=True);start=time.perf_counter();subprocess.run(cmd,env=env,check=True,timeout=120);return time.perf_counter()-start
if not a.run_only:
 out.mkdir(parents=True,exist_ok=False)
 run([str(root/".venv/Scripts/python.exe"),"tools/lower_intrinsics.py","local/compiler-spike/initial/function.ll",str(out/"lowered.ll")])
 run([clang,"-c","-march=haswell","native/remill_oracle.S","-o",str(out/"oracle.obj")])
 common=[cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include"]
 run([*common,"native/remill_loop_test.cpp",f"/Fo{out}/test.obj"])
 run([*common,"native/remill_benchmark.cpp",f"/Fo{out}/bench.obj"])
 builds=[]
 for label,source in (("helpers",root/"local/compiler-spike/initial/function.bc"),("lowered",out/"lowered.ll")):
  obj=out/f"{label}.obj";cmd=[clang,"-c","-O2","-march=haswell",str(source),"-o",str(obj)]
  elapsed=run(cmd)
  for name,main in (("test","test.obj"),("bench","bench.obj")):
   run([cxx,"/nologo",str(out/main),str(out/"oracle.obj"),str(obj),f"/Fe{out}/{label}-{name}.exe"])
  run([str(out/f"{label}-test.exe"),str(root/"local/compiler-spike/initial/original.bin")])
  before=hashlib.sha256(obj.read_bytes()).hexdigest();incremental=run(cmd);after=hashlib.sha256(obj.read_bytes()).hexdigest()
  builds.append(dict(label=label,compile_seconds=elapsed,incremental_seconds=incremental,object_bytes=obj.stat().st_size,sha256=after,identical_rebuild=before==after))
 (out/"builds.json").write_text(json.dumps(builds,indent=2)+"\n")
else:
 summary=[]
 for label in ("helpers","lowered"):
  cmd=[str(out/f"{label}-bench.exe"),str(root/"local/compiler-spike/initial/original.bin")]
  with (out/f"{label}.jsonl").open("wb") as o,(out/f"{label}.stderr").open("wb") as e:
   r=subprocess.run(cmd,stdout=o,stderr=e,env=env,timeout=120)
  if r.returncode:raise RuntimeError(f"{label} benchmark failed {r.returncode}")
  rows=[json.loads(line) for line in (out/f"{label}.jsonl").read_text().splitlines()]
  import statistics
  for length in (1,8,64):
   values=[x for x in rows if x["length"]==length]
   summary.append(dict(label=label,length=length,median_ratio=statistics.median(x["ratio"] for x in values),median_native_ns=statistics.median(x["native_ns"] for x in values),median_aot_ns=statistics.median(x["aot_ns"] for x in values)))
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary),flush=True)
