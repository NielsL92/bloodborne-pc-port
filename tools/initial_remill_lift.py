import json,subprocess
from pathlib import Path
from tools.formats import ElfImage
ROOT=Path.cwd()
out=ROOT/"local/compiler-spike/initial";out.mkdir(parents=True,exist_ok=True)
image=ElfImage((ROOT/"local/update/uroot/eboot.bin").read_bytes())
address=0x3360
fn=next(f for f in image.unwind_functions() if f["start"]==address)
code=image.at_va(address,fn["size"])
cmd=[str(ROOT/"build/remill/bin/lift/remill-lift-21.exe"),"--os=windows","--arch=amd64_avx",f"--address={0x100000000+address}",f"--bytes={code.hex()}",f"--bc_out={out/'function.bc'}",f"--ir_out={out/'function.ll'}"]
(out/"command.json").write_text(json.dumps(cmd,indent=2)+"\n")
subprocess.run(cmd,check=True)
print("lifted real loop",hex(address),fn["size"],"bytes")
