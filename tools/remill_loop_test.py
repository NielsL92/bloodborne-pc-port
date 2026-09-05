"""Build and run the first real whole-function Remill differential experiment."""
import json,subprocess
from pathlib import Path
from tools.dev import environment,LLVM
from tools.formats import ElfImage
ROOT=Path.cwd();out=ROOT/"local/compiler-spike/initial"
env=environment()
image=ElfImage((ROOT/"local/update/uroot/eboot.bin").read_bytes())
(out/"original.bin").write_bytes(image.at_va(0x3360,42))
cxx=str(LLVM/"bin/clang-cl.exe");clang=str(LLVM/"bin/clang.exe")
commands=[
 [clang,"-c","-O2","-march=haswell",str(out/"function.bc"),"-o",str(out/"function.obj")],
 [clang,"-c","-march=haswell","native/remill_oracle.S","-o",str(out/"oracle.obj")],
 [cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_loop_test.cpp",f"/Fo{out}/harness.obj"],
 [cxx,"/nologo",str(out/"harness.obj"),str(out/"function.obj"),str(out/"oracle.obj"),f"/Fe{out}/loop-test.exe"],
 [str(out/"loop-test.exe"),str(out/"original.bin")],
]
for cmd in commands:
 print(json.dumps(cmd),flush=True);subprocess.run(cmd,env=env,cwd=ROOT,check=True,timeout=120)
