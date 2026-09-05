"""Install pinned official portable P3 tools under the workspace, verifying every archive."""
import concurrent.futures,hashlib,json,urllib.request,zipfile
from pathlib import Path
items=[
 dict(name="ghidra-12.1.3",archive="ghidra_12.1.3_PUBLIC_20260817.zip",size=569445154,
 sha256="93a5d11a9ad510622acaaf908c556a7b9b764d338e78a7567f3689bf5081fd54",
 url="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.3_build/ghidra_12.1.3_PUBLIC_20260817.zip"),
 dict(name="temurin-21.0.12.1",archive="OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip",size=205073461,
 sha256="f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e",
 url="https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip")]
root=Path.cwd();downloads=root/"local/downloads/p3";downloads.mkdir(parents=True,exist_ok=False)
def download(item):
 p=downloads/item["archive"];digest=hashlib.sha256();size=0
 with urllib.request.urlopen(urllib.request.Request(item["url"],headers={"User-Agent":"Bloodborne-local-recompilation-investigation"}),timeout=60) as src,p.open("xb") as dst:
  while data:=src.read(1024*1024):
   dst.write(data);digest.update(data);size+=len(data)
 if size!=item["size"] or digest.hexdigest()!=item["sha256"]:raise RuntimeError("archive verification failed: "+item["name"])
 print(json.dumps(dict(download=item["name"],verified=True,bytes=size)),flush=True)
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 archives=list(pool.map(download,items))
for item,p in zip(items,archives):
 out=root/"external/toolchains"/item["name"];out.mkdir(exist_ok=False)
 with zipfile.ZipFile(p) as z:
  for member in z.infolist():
   target=(out/member.filename).resolve()
   if not target.is_relative_to(out.resolve()):raise RuntimeError("archive escaped output")
  z.extractall(out)
 item["installed_to"]=str(out)
 print(json.dumps(dict(extracted=item["name"],path=str(out))),flush=True)
(root/"reports/p3-tool-downloads.json").write_bytes((json.dumps(items,indent=2)+"\n").encode())
