"""Six additional real whole-function/closed-graph contracts; fresh output only."""
import hashlib,json,subprocess,sys
from pathlib import Path
from tools.dev import environment,LLVM
from tools.formats import ElfImage
ROOT=Path.cwd();out=ROOT/(sys.argv[1] if len(sys.argv)>1 else "local/compiler-spike/graphs");out.mkdir(parents=True,exist_ok=False);env=environment()
rvas=(0x2550,0x65d0,0xb820,0x2fa30,0x3df50,0x3240,0x5e4e0,0x77e80,0x2b2b0)
image=ElfImage((ROOT/"local/update/uroot/eboot.bin").read_bytes());ranges={f["start"]:f for f in image.unwind_functions()}
clang=str(LLVM/"bin/clang.exe");cxx=str(LLVM/"bin/clang-cl.exe");objects=[];manifest=[]
def run(cmd):
 print(json.dumps(cmd),flush=True);subprocess.run(cmd,env=env,check=True,timeout=120)
for rva in rvas:
 folder=out/f"{rva:x}";folder.mkdir();f=ranges[rva];raw=folder/"original.bin";raw.write_bytes(image.at_va(rva,f["size"]))
 cmd=[str(ROOT/"build/remill/bin/lift/remill-lift-21.exe"),"--os=windows","--arch=amd64_avx",f"--address={0x100000000+rva}",f"--bytes_file={raw}",f"--bc_out={folder/'function.bc'}",f"--ir_out={folder/'function.ll'}"]
 run(cmd)
 obj=folder/"function.obj";run([clang,"-c","-O2","-march=haswell",str(folder/"function.bc"),"-o",str(obj)]);objects.append(str(obj))
 manifest.append(dict(rva=rva,size=f["size"],sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),argv=cmd))
(out/"inputs.json").write_text(json.dumps(manifest,indent=2)+"\n")
run([clang,"-c","-march=haswell","native/remill_oracle.S","-o",str(out/"oracle.obj")])
run([cxx,"/nologo","/c","/O2","/EHsc","/arch:AVX2","/std:c++17","/DADDRESS_SIZE_BITS=64","/DHAS_FEATURE_AVX=1","/DHAS_FEATURE_AVX512=0","/clang:-mlong-double-80","/Iexternal/remill/include","native/remill_graph_test.cpp",f"/Fo{out}/harness.obj"])
run([cxx,"/nologo",str(out/"harness.obj"),str(out/"oracle.obj"),*objects,f"/Fe{out}/graph-test.exe"])
summary=[]
for rva in rvas[:6]:
 folder=out/f"{rva:x}";cmd=[str(out/"graph-test.exe"),str(out),f"{rva:x}"]
 with (folder/"test.stdout").open("wb") as o,(folder/"test.stderr").open("wb") as e:r=subprocess.run(cmd,stdout=o,stderr=e,timeout=120)
 lines=(folder/"test.stdout").read_text().splitlines()
 record=dict(rva=hex(rva),argv=cmd,exit=r.returncode,summary=json.loads(lines[-1]) if lines else None)
 summary.append(record);print(json.dumps(record),flush=True)
(out/"test-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
raise SystemExit(any(r["exit"] for r in summary))
