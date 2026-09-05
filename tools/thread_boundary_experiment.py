"""Authored TLS and locked-operation boundary experiment, with checked memory helpers."""
import hashlib,json,subprocess,sys,shutil
from pathlib import Path
from tools.dev import environment,LLVM
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);env=environment()
def run(cmd,name):
 with (out/(name+".stdout")).open("wb") as o,(out/(name+".stderr")).open("wb") as e:
  r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=120)
 print(json.dumps(dict(step=name,exit=r.returncode)),flush=True)
 if r.returncode:raise RuntimeError(name+" failed")
clang=LLVM/"bin/clang.exe";cxx=LLVM/"bin/clang-cl.exe";opt=LLVM/"bin/opt.exe"
shutil.copy2("build/state-promotion/bb-state-promotion.exe",out/"promotion.exe")
for name,address in [("tls",0x1002000000),("atomic",0x1002000100),("publish",0x1002000200),("consume",0x1002000300)]:
 d=out/name;d.mkdir()
 run([clang,"-c",f"native/thread_{name}.S","-o",d/"original.obj"],name+"-assemble")
 run([LLVM/"bin/llvm-objcopy.exe","--dump-section",f".text={d}/original.bin",d/"original.obj",d/"copy.obj"],name+"-bytes")
 run(["build/remill/bin/lift/remill-lift-21.exe","--os=windows","--arch=amd64_avx",f"--address={address}",f"--bytes_file={d}/original.bin",f"--bc_out={d}/function.bc",f"--ir_out={d}/function.ll"],name+"-lift")
 # Keep memory/atomic/barrier operations external. Ordinary memory lowering is forbidden here.
 run([opt,"-S","-passes=default<O2>",d/"function.ll","-o",d/"canonical.ll"],name+"-canonical")
 run([out/"promotion.exe",d/"canonical.ll",d/"promoted.ll"],name+"-promote")
 run([clang,"-c","-O2","-march=haswell",d/"promoted.ll","-o",d/"function.obj"],name+"-object")
run([cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++20","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_thread_test.cpp",f"/Fo{out}/harness.obj"],"harness")
run([cxx,"/nologo",out/"harness.obj",out/"tls/function.obj",out/"atomic/function.obj",out/"publish/function.obj",out/"consume/function.obj",f"/Fe{out}/test.exe"],"link")
run([out/"test.exe",out],"contracts")
(out/"summary.json").write_bytes((out/"contracts.stdout").read_bytes())
(out/"sha256.json").write_bytes((json.dumps({str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob("*") if f.is_file()},indent=2)+"\n").encode())
