"""Run a tool in this project's pinned Windows compiler environment."""
import argparse
import os
from pathlib import Path
import subprocess
import shutil

ROOT=Path(__file__).resolve().parents[1]
LLVM=ROOT/"external/toolchains/llvm-21.1.8/clang+llvm-21.1.8-x86_64-pc-windows-msvc"
CMAKE=ROOT/"external/toolchains/cmake-4.2.3/cmake-4.2.3-windows-x86_64"
NINJA=ROOT/"external/toolchains/ninja-1.13.2"
VCVARS=Path("C:/Program Files (x86)/Microsoft Visual Studio/18/BuildTools/VC/Auxiliary/Build/vcvars64.bat")

def environment():
    if not VCVARS.is_file():
        raise RuntimeError(f"Missing MSVC x64 environment: {VCVARS}")
    command=f'call "{VCVARS}" >nul && set'
    r=subprocess.run('cmd.exe /d /s /c "' + command + '"', capture_output=True,text=True)
    if r.returncode:
        raise RuntimeError(f"vcvars64 failed: {r.stderr}")
    env=os.environ.copy()
    for line in r.stdout.splitlines():
        if "=" in line and not line.startswith("="):
            k,v=line.split("=",1)
            env[k]=v
    oldpath=next(v for k,v in env.items() if k.lower()=="path")
    env={k:v for k,v in env.items() if k.lower()!="path"}
    env["PATH"]=os.pathsep.join(map(str,[LLVM/"bin", CMAKE/"bin",NINJA,ROOT/".venv/Scripts"]))+os.pathsep+oldpath
    env["CMAKE_BUILD_PARALLEL_LEVEL"]="2"
    return env

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fast-git-metadata",action="store_true")
    p.add_argument("command",nargs=argparse.REMAINDER)
    a=p.parse_args()
    cmd=a.command[1:] if a.command[:1]==["--"] else a.command
    if not cmd:
        p.error("command is required")
    env=environment()
    if a.fast_git_metadata:
        env.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="diff.ignoreSubmodules",GIT_CONFIG_VALUE_0="dirty")
    cmd[0]=shutil.which(cmd[0],path=env["PATH"]) or cmd[0]
    raise SystemExit(subprocess.run(cmd,env=env,cwd=ROOT).returncode)
