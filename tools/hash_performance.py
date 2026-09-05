"""Build, validate, then separately time helper and contract-lowered AOT."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from tools.dev import environment,LLVM
p=argparse.ArgumentParser();p.add_argument("--run-only",action="store_true");a=p.parse_args()
root=Path.cwd();out=root/"local/compiler-spike/hash-performance";env=environment();clang=str(LLVM/"bin/clang.exe");cxx=str(LLVM/"bin/clang-cl.exe")
def run(cmd):
 print(json.dumps(cmd),flush=True);start=time.perf_counter();subprocess.run(cmd,env=env,check=True,timeout=120);return time.perf_counter()-start
if not a.run_only:
 out.mkdir(parents=True,exist_ok=False)
 for rva in ("2fa30","5e4e0"):
  run([str(root/".venv/Scripts/python.exe"),"tools/lower_intrinsics.py",f"local/compiler-spike/graphs-return-count/{rva}/function.ll",str(out/f"{rva}-lowered.ll")])
 run([clang,"-c","-march=haswell","native/remill_oracle.S","-o",str(out/"oracle.obj")])
 common=[cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include"]
 run([*common,"native/remill_graph_test.cpp",f"/Fo{out}/test.obj"])
 run([*common,"native/remill_hash_benchmark.cpp",f"/Fo{out}/bench.obj"])
 builds=[]
 for label in ("helpers","lowered"):
  objects=[];elapsed=0
  for rva in ("2550","65d0","b820","2fa30","3df50","3240","5e4e0","77e80","2b2b0"):
   if rva in ("2fa30","5e4e0"):
    source=root/f"local/compiler-spike/graphs-return-count/{rva}/function.bc" if label=="helpers" else out/f"{rva}-lowered.ll"
    obj=out/f"{rva}-{label}.obj";elapsed+=run([clang,"-c","-O2","-march=haswell",str(source),"-o",str(obj)])
   else:obj=root/f"local/compiler-spike/graphs-return-count/{rva}/function.obj"
   objects.append(str(obj))
  for name,main in (("test","test.obj"),("bench","bench.obj")):
   run([cxx,"/nologo",str(out/main),str(out/"oracle.obj"),*objects,f"/Fe{out}/{label}-{name}.exe"])
  run([str(out/f"{label}-test.exe"),str(root/"local/compiler-spike/graphs-return-count"),"2fa30"])
  builds.append(dict(label=label,compile_seconds=elapsed))
 (out/"builds.json").write_text(json.dumps(builds,indent=2)+"\n")
else:
 summary=[]
 for label in ("helpers","lowered"):
  cmd=[str(out/f"{label}-bench.exe"),str(root/"local/compiler-spike/graphs-return-count")]
  with (out/f"{label}.jsonl").open("wb") as o,(out/f"{label}.stderr").open("wb") as e:
   r=subprocess.run(cmd,stdout=o,stderr=e,env=env,timeout=120)
  if r.returncode:raise RuntimeError(f"{label} benchmark failed {r.returncode}")
  rows=[json.loads(line) for line in (out/f"{label}.jsonl").read_text().splitlines()]
  import statistics
  for length in (8,64,1024):
   values=[x for x in rows if x["length"]==length]
   summary.append(dict(label=label,length=length,median_ratio=statistics.median(x["ratio"] for x in values),median_native_ns=statistics.median(x["native_ns"] for x in values),median_aot_ns=statistics.median(x["aot_ns"] for x in values)))
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary),flush=True)
