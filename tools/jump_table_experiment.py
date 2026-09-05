"""Real bit-reader function: recover its five table entries and preserve RIP-relative data."""
import hashlib,json,struct,subprocess,sys,shutil
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.formats import ElfImage
from tools.dev import environment,LLVM
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);env=environment()
raw=Path("local/update/uroot/eboot.bin").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9"
im=ElfImage(raw);fn=next(x for x in im.unwind_functions() if x["start"]==0x401f0)
assert fn["size"]==412
body=im.at_va(fn["start"],fn["size"]);(out/"original.bin").write_bytes(body)
global_bytes=im.at_va(0x2bc0f50,33);(out/"global.bin").write_bytes(global_bytes)
assert list(global_bytes)==[0]+[(n+7)//8 for n in range(1,33)]
table=im.at_va(0x40378,20);targets=[0x40378+x for x in struct.unpack("<5i",table)]
assert targets==[0x4034d,0x4023c,0x40264,0x40292,0x402c8]
decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for addr in targets:
 assert 0x401f0<=addr<0x40376 and list(decoder.disasm(im.at_va(addr,16),addr))
def run(cmd,name):
 with (out/(name+".stdout")).open("wb") as o,(out/(name+".stderr")).open("wb") as e:
  r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=120)
 print(json.dumps(dict(step=name,exit=r.returncode)),flush=True)
 if r.returncode:raise RuntimeError(name+" failed")
clang=LLVM/"bin/clang.exe";cxx=LLVM/"bin/clang-cl.exe";opt=LLVM/"bin/opt.exe"
shutil.copy2("build/state-promotion/bb-state-promotion.exe",out/"promotion.exe")
entries=[0x401f0,*targets];objects=[]
for addr in entries:
 d=out/f"{addr:x}";d.mkdir();(d/"bytes.bin").write_bytes(im.at_va(addr,0x40378-addr))
 run(["build/remill/bin/lift/remill-lift-21.exe","--os=windows","--arch=amd64_avx",f"--address={0x100000000+addr}",f"--bytes_file={d}/bytes.bin",f"--bc_out={d}/function.bc",f"--ir_out={d}/function.ll"],f"{addr:x}-lift")
 run([sys.executable,"tools/lower_intrinsics.py",d/"function.ll",d/"lowered.ll"],f"{addr:x}-lower")
 run([opt,"-S","-passes=default<O2>",d/"lowered.ll","-o",d/"canonical.ll"],f"{addr:x}-canonical")
 run([out/"promotion.exe",d/"canonical.ll",d/"promoted.ll"],f"{addr:x}-promote")
 run([clang,"-c","-O2","-march=haswell",d/"promoted.ll","-o",d/"function.obj"],f"{addr:x}-object")
 objects.append(d/"function.obj")
run([clang,"-c","-march=haswell","native/remill_oracle.S","-o",out/"oracle.obj"],"oracle")
run([cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_jump_test.cpp",f"/Fo{out}/harness.obj"],"harness")
run([cxx,"/nologo",out/"harness.obj",out/"oracle.obj",*objects,f"/Fe{out}/test.exe"],"link")
run([out/"test.exe",out],"contracts")
(out/"summary.json").write_bytes((out/"contracts.stdout").read_bytes())
(out/"recovery.json").write_bytes((json.dumps(dict(module_sha256=hashlib.sha256(raw).hexdigest(),function=fn,table_rva=0x40378,table_sha256=hashlib.sha256(table).hexdigest(),targets=targets,global_rva=0x2bc0f50,global_sha256=hashlib.sha256(global_bytes).hexdigest(),method="bounded table interpretation and target decoding; five statically compiled trace entries, no runtime lifting or original CPU fallback"),indent=2)+"\n").encode())
(out/"sha256.json").write_bytes((json.dumps({str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob("*") if f.is_file()},indent=2)+"\n").encode())
