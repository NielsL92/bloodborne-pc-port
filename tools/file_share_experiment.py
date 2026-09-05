"""Isolate sharing violations from ACL denial on a new owned fixture."""
import hashlib,json,subprocess,sys
from pathlib import Path
from tools.dev import environment,LLVM
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
env=environment()
for name,cmd in [
 ("build",[LLVM/"bin/clang-cl.exe","/nologo","/O2","native/file_share_probe.cpp",f"/Fo{out}/probe.obj",f"/Fe{out}/probe.exe"]),
 ("probe",[out/"probe.exe",(out/"fixture.bin").resolve()])]:
 with (out/(name+".stdout")).open("wb") as o,(out/(name+".stderr")).open("wb") as e:
  r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=60)
 if r.returncode:raise RuntimeError(f"{name} exit {r.returncode}")
summary=[json.loads(x) for x in (out/"probe.stdout").read_text().splitlines()]
(out/"summary.json").write_bytes((json.dumps(summary,indent=2)+"\n").encode())
print(json.dumps(summary))
