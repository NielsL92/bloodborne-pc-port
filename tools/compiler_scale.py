"""Resume a stratified Remill/LLVM object-build survey; compilation is not execution coverage."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import time
from tools.dev import environment,LLVM
from tools.formats import ElfImage
ROOT=Path(__file__).resolve().parents[1]
class Counters(ctypes.Structure):
    _fields_=[("cb",ctypes.c_ulong),("faults",ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ("peak_working_set","working_set","peak_paged_pool","paged_pool","peak_nonpaged_pool","nonpaged_pool","pagefile","peak_pagefile")]
getmem=ctypes.windll.psapi.GetProcessMemoryInfo
getmem.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_ulong]
getmem.restype=ctypes.c_int
def sha(f):
    with Path(f).open("rb") as s:return hashlib.file_digest(s,"sha256").hexdigest()
def measured(cmd,folder,name,env,timeout):
    start=time.monotonic();peak=0
    with (folder/f"{name}.stdout").open("wb") as out,(folder/f"{name}.stderr").open("wb") as err:
        proc=subprocess.Popen(cmd,stdout=out,stderr=err,cwd=ROOT,env=env)
        reason=None
        while proc.poll() is None:
            counters=Counters();counters.cb=ctypes.sizeof(counters)
            if getmem(int(proc._handle),ctypes.byref(counters),ctypes.sizeof(counters)):
                peak=max(peak,counters.peak_working_set)
            if peak>4*1024**3:
                reason="4 GiB per-process memory bound";proc.kill()
            if time.monotonic()-start>timeout:
                reason=f"{timeout}s bound";proc.kill()
            try:proc.wait(timeout=0.2)
            except subprocess.TimeoutExpired:pass
        counters=Counters();counters.cb=ctypes.sizeof(counters)
        if getmem(int(proc._handle),ctypes.byref(counters),ctypes.sizeof(counters)):
            peak=max(peak,counters.peak_working_set)
    return dict(argv=cmd,exit=proc.returncode,elapsed_seconds=time.monotonic()-start,
                peak_working_set_bytes=peak,bound_failure=reason)
def main():
    p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=1000);p.add_argument("--timeout",type=int,default=60)
    p.add_argument("--out",default="local/compiler-spike/scale-default");a=p.parse_args()
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    lifter=ROOT/"build/remill/bin/lift/remill-lift-21.exe";clang=LLVM/"bin/clang.exe"
    source=ROOT/"local/update/uroot/eboot.bin"
    candidates=json.loads((ROOT/"local/compiler-spike/candidates.json").read_text())
    identity=dict(input_sha256=sha(source),lifter_sha256=sha(lifter),clang_sha256=sha(clang),
                  patch_sha256=sha(ROOT/"patches/remill-windows-sdk.patch"),timeout=a.timeout,
                  flags=["amd64_avx","windows","O2","march=haswell"],seed=candidates["seed"])
    lock=out/"identity.json"
    if lock.exists() and json.loads(lock.read_text())!=identity:raise RuntimeError("Build identity changed; use a new output directory")
    lock.write_text(json.dumps(identity,indent=2)+"\n")
    assert identity["input_sha256"]==candidates["input_sha256"]
    groups=defaultdict(list)
    for fn in candidates["scaling_batch"]:groups[fn["stratum"]].append(fn)
    selected=[]
    for i in range(max(map(len,groups.values()))):
        for group in groups.values():
            if i<len(group):selected.append(group[i])
    image=ElfImage(source.read_bytes());env=environment();results=[];begin=time.monotonic()
    for fn in selected[:a.limit]:
        folder=out/f'{fn["start"]:x}';folder.mkdir(exist_ok=True)
        path=folder/"result.json"
        if path.exists():
            previous=json.loads(path.read_text())
            obj=folder/"function.obj"
            if previous["status"]=="object_built" and (not obj.exists() or sha(obj)!=previous["object_sha256"]):raise RuntimeError("Cached object changed")
            results.append(previous);continue
        raw=folder/"original.bin";raw.write_bytes(image.at_va(fn["start"],fn["size"]))
        bc=folder/"function.bc";ir=folder/"function.ll";obj=folder/"function.obj"
        result=dict(start=fn["start"],size=fn["size"],stratum=fn["stratum"],input_range_sha256=sha(raw),
                    capstone_linear_decode=fn["decode"] is not None,features=fn["decode"]["tags"] if fn["decode"] else [])
        result["lift"]=measured([str(lifter),"--arch=amd64_avx","--os=windows",f"--address={0x100000000+fn['start']}",f"--bytes_file={raw}",f"--bc_out={bc}",f"--ir_out={ir}"],folder,"lift",env,a.timeout)
        result["status"]="lift_failed"
        if result["lift"]["exit"]==0:
            import re
            declarations=re.findall(r"^declare[^@]*@([^ (]+)",ir.read_text(),re.M)
            result["declared_intrinsics"]=[s for s in declarations if s.startswith("__remill_")]
            result["external_compiled_entries"]=[s for s in declarations if s.startswith("sub_")]
            result["unresolved_cpu_boundaries"]=[s for s in declarations if s in ("__remill_missing_block","__remill_error","__remill_async_hyper_call","__remill_sync_hyper_call","__remill_jump","__remill_function_call")]
            result["compile"]=measured([str(clang),"-c","-O2","-march=haswell",str(bc),"-o",str(obj)],folder,"compile",env,a.timeout)
            result["status"]="object_built" if result["compile"]["exit"]==0 else "object_failed"
            if result["status"]=="object_built":
                result.update(object_bytes=obj.stat().st_size,object_sha256=sha(obj))
        path.write_text(json.dumps(result,indent=2)+"\n")
        results.append(result)
        if len(results)%10==0:print(json.dumps(dict(done=len(results),status=dict(Counter(r["status"] for r in results)))),flush=True)
    summary=dict(status="survey_complete_not_execution_validation",attempted=len(results),
                 results=dict(Counter(r["status"] for r in results)),elapsed_this_invocation=time.monotonic()-begin,
                 total_recorded_lift_seconds=sum(r["lift"]["elapsed_seconds"] for r in results),
                 total_recorded_compile_seconds=sum(r.get("compile",{}).get("elapsed_seconds",0) for r in results),
                 peak_working_set_bytes=max((max(r["lift"]["peak_working_set_bytes"],r.get("compile",{}).get("peak_working_set_bytes",0)) for r in results),default=0),
                 object_bytes=sum(r.get("object_bytes",0) for r in results),
                 objects_with_unresolved_cpu_boundaries=sum(bool(r.get("unresolved_cpu_boundaries")) for r in results),
                 per_function_results=[str(out/f'{r["start"]:x}'/"result.json") for r in results])
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!="per_function_results"},indent=2))
if __name__=="__main__":main()
