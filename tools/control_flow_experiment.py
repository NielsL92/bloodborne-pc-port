"""Build and test authored native service/callback/nonlocal-control contracts."""
import hashlib,json,subprocess,sys,shutil
from pathlib import Path
from tools.dev import environment,LLVM
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False);env=environment()
def run(cmd,name,expected=0):
    with (out/(name+".stdout")).open("wb") as o,(out/(name+".stderr")).open("wb") as e:
        result=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=120)
    print(json.dumps(dict(step=name,exit=result.returncode)),flush=True)
    if expected is None:
        if result.returncode==0:raise RuntimeError(name+" unexpectedly passed")
    elif result.returncode!=expected:raise RuntimeError(name+" failed; inspect preserved evidence")
    return result.returncode
clang=LLVM/"bin/clang.exe";cxx=LLVM/"bin/clang-cl.exe";opt=LLVM/"bin/opt.exe"
shutil.copy2(root/"build/state-promotion/bb-state-promotion.exe",out/"promotion.exe")
for name,address in [("root",0x1001000000),("callback",0x1001000100)]:
    d=out/name;d.mkdir()
    run([clang,"-c",f"native/control_{name}.S","-o",d/"original.obj"],name+"-assemble")
    run([LLVM/"bin/llvm-objcopy.exe","--dump-section",f".text={d}/original.bin",d/"original.obj",d/"copy.obj"],name+"-bytes")
    run([root/"build/remill/bin/lift/remill-lift-21.exe","--os=windows","--arch=amd64_avx",f"--address={address}",f"--bytes_file={d}/original.bin",f"--bc_out={d}/function.bc",f"--ir_out={d}/function.ll"],name+"-lift")
    run([sys.executable,"tools/lower_intrinsics.py",d/"function.ll",d/"lowered.ll"],name+"-lower")
    run([opt,"-S","-passes=default<O2>",d/"lowered.ll","-o",d/"canonical.ll"],name+"-canonical")
    for label,options in [("guarded",["--control-exits"]),("unguarded",[])]:
        run([out/"promotion.exe",d/"canonical.ll",d/(label+".ll"),*options],name+"-"+label)
        run([clang,"-c","-O2","-march=haswell",d/(label+".ll"),"-o",d/(label+".obj")],name+"-"+label+"-object")
fixture_hash=hashlib.sha256((out/"root/original.bin").read_bytes()+(out/"callback/original.bin").read_bytes()).hexdigest()
run([cxx,f'/DFIXTURE_SHA256="{fixture_hash}"',"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_control_test.cpp",f"/Fo{out}/harness.obj"],"harness")
for label in ["guarded","unguarded"]:
    run([cxx,"/nologo",out/"harness.obj",out/"root"/(label+".obj"),out/"callback"/(label+".obj"),f"/Fe{out}/{label}.exe"],label+"-link")
run([out/"guarded.exe",out],"positive-contract")
run([out/"guarded.exe",out,"--unknown"],"unknown-target",expected=4)
run([out/"unguarded.exe",out,"--negative-only"],"missing-guard-regression",expected=3221225477)
negative=(out/"missing-guard-regression.stderr").read_text()
assert "phase=aot case=0" in negative and "access=1 address=0x1001000000" in negative, negative
summary=json.loads((out/"positive-contract.stdout").read_text().splitlines()[-1])
summary["fixture_sha256"]=fixture_hash
summary["unknown_target_exit"]=4
summary["missing_guard_exit"]=3221225477
summary["missing_guard_rejected"]=True
(out/"summary.json").write_bytes((json.dumps(summary,indent=2)+"\n").encode("utf-8"))
(out/"sha256.json").write_bytes((json.dumps({str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob("*") if f.is_file()},indent=2)+"\n").encode("utf-8"))
