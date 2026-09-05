import json,subprocess,sys
from pathlib import Path
from tools.formats import ElfImage
ROOT=Path.cwd();out=ROOT/(sys.argv[1] if len(sys.argv)>1 else "local/compiler-spike/varied");out.mkdir(parents=True,exist_ok=False)
image=ElfImage((ROOT/"local/update/uroot/eboot.bin").read_bytes())
ranges={f["start"]:f for f in image.unwind_functions()}
for address in (0x1a50,0x3500,0x3530):
 f=ranges[address];folder=out/f"{address:x}";folder.mkdir(exist_ok=True)
 raw=folder/"original.bin";raw.write_bytes(image.at_va(address,f["size"]))
 cmd=[str(ROOT/"build/remill/bin/lift/remill-lift-21.exe"),"--os=windows","--arch=amd64_avx",f"--address={0x100000000+address}",f"--bytes_file={raw}",f"--bc_out={folder/'function.bc'}",f"--ir_out={folder/'function.ll'}"]
 (folder/"command.json").write_text(json.dumps(cmd,indent=2)+"\n")
 subprocess.run(cmd,check=True,timeout=60)
 print(hex(address),f["size"])
