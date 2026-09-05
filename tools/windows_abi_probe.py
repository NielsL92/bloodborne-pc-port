"""Compile authored LLVM IR to COFF, link a Windows host caller and execute."""
import hashlib
import json
import subprocess
from pathlib import Path
from tools.dev import environment,LLVM
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"build/windows-abi-probe"
out.mkdir(parents=True,exist_ok=True)
env=environment()
commands=[
    [str(LLVM/"bin/clang.exe"),"-c","-O2","-target","x86_64-pc-windows-msvc","native/windows_abi_probe.ll","-o",str(out/"probe.obj")],
    [str(LLVM/"bin/clang-cl.exe"),"/nologo","/c","/O2","/EHsc","/arch:AVX2","native/windows_abi_probe.cpp",f"/Fo{out}/host.obj"],
    [str(LLVM/"bin/clang-cl.exe"),"/nologo",str(out/"host.obj"),str(out/"probe.obj"),f"/Fe{out}/probe.exe"],
    [str(out/"probe.exe")],
    [str(LLVM/"bin/llvm-readobj.exe"),"--file-headers",str(out/"probe.obj")],
    [str(LLVM/"bin/llvm-objdump.exe"),"-d",str(out/"probe.obj")],
]
for cmd in commands:
    print(json.dumps(cmd),flush=True)
    subprocess.run(cmd,env=env,cwd=ROOT,check=True)
for f in out.iterdir():
    if f.is_file():
        print(f.name,hashlib.sha256(f.read_bytes()).hexdigest())
