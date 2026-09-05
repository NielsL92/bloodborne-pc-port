"""Build the three real SIMD/FP contracts and preserve every pass/failure."""
import json,subprocess,sys
from pathlib import Path
from tools.dev import environment,LLVM
ROOT=Path.cwd();out=ROOT/(sys.argv[1] if len(sys.argv)>1 else "local/compiler-spike/varied");env=environment()
clang=str(LLVM/"bin/clang.exe");cxx=str(LLVM/"bin/clang-cl.exe")
objects=[]
for rva in (0x1a50,0x3500,0x3530):
 folder=out/f"{rva:x}";obj=folder/"function.obj";objects.append(str(obj))
 cmd=[clang,"-c","-O2","-march=haswell",str(folder/"function.bc"),"-o",str(obj)]
 print(json.dumps(cmd),flush=True);subprocess.run(cmd,env=env,check=True)
commands=[
 [clang,"-c","-march=haswell","native/remill_oracle.S","-o",str(out/"oracle.obj")],
 [cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_varied_test.cpp",f"/Fo{out}/harness.obj"],
 [cxx,"/nologo",str(out/"harness.obj"),str(out/"oracle.obj"),*objects,f"/Fe{out}/varied-test.exe"]
]
for cmd in commands:
 print(json.dumps(cmd),flush=True);subprocess.run(cmd,env=env,check=True)
summary=[]
for rva in (0x1a50,0x3500,0x3530):
 folder=out/f"{rva:x}"
 cmd=[str(out/"varied-test.exe"),str(folder/"original.bin"),f"{rva:x}"]
 with (folder/"test.stdout").open("wb") as o,(folder/"test.stderr").open("wb") as e:
  result=subprocess.run(cmd,env=env,stdout=o,stderr=e,timeout=120)
 lines=(folder/"test.stdout").read_text().splitlines()
 record=dict(rva=hex(rva),argv=cmd,exit=result.returncode,summary=json.loads(lines[-1]) if lines else None)
 summary.append(record);print(json.dumps(record),flush=True)
(out/"test-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
raise SystemExit(any(r["exit"]!=0 for r in summary))
