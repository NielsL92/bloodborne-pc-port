"""Verify third-party patch series on copied files, leaving checkout and evidence unchanged."""
import json,re,shutil,subprocess,sys
from pathlib import Path
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
series={
 "shadPS4":["shadps4-research-capture.patch","shadps4-research-ime.patch","shadps4-research-diagnostics.patch","shadps4-guest-file-sharing.patch"],
 "remill":["remill-windows-sdk.patch"],
 "tracy-tools":["tracy-tools-csvexport.patch"]}
records=[]
for name,patches in series.items():
 target=out/name;target.mkdir()
 subprocess.run(["git","init","--quiet",str(target)],check=True)
 paths=set()
 for patch in patches:
  for line in (root/"patches"/patch).read_text().splitlines():
   if line.startswith("+++ b/"):paths.add(line[6:])
 for p in paths:
  source=root/"external"/name/p
  if source.exists():
   dest=target/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 for patch in reversed(patches):
  command=["git","apply","--reverse","--whitespace=nowarn",str(root/"patches"/patch)]
  r=subprocess.run(command,cwd=target,capture_output=True)
  records.append(dict(repo=name,patch=patch,direction="reverse",exit=r.returncode,stderr=r.stderr.decode(errors="replace")))
  if r.returncode:raise RuntimeError(records[-1])
 # A successful reverse must equal the pinned upstream bytes, not just exit zero.
 for p in paths:
  repo=root/"external"/name
  original=subprocess.run(["git","-c",f"safe.directory={repo.as_posix()}","-C",str(repo),"show",f"HEAD:{p}"],capture_output=True)
  if original.returncode==0:
   assert (target/p).read_bytes().replace(b"\r\n",b"\n")==original.stdout.replace(b"\r\n",b"\n"),("reverse did not restore upstream",name,p)
  else:assert not (target/p).exists(),("new file survived reverse",name,p)
 for patch in patches:
  r=subprocess.run(["git","apply","--whitespace=nowarn",str(root/"patches"/patch)],cwd=target,capture_output=True)
  records.append(dict(repo=name,patch=patch,direction="forward",exit=r.returncode,stderr=r.stderr.decode(errors="replace")))
  if r.returncode:raise RuntimeError(records[-1])
 for p in paths:
  a=root/"external"/name/p;b=target/p
  if a.exists():assert a.read_bytes().replace(b"\r\n",b"\n")==b.read_bytes().replace(b"\r\n",b"\n"),p
(out/"summary.json").write_bytes((json.dumps(records,indent=2)+"\n").encode())
print(json.dumps(dict(status="pass",patch_applications=len(records),copied_only=True)))
