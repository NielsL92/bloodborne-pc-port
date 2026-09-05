"""Extract named package system metadata twice, then create an immutable v2 overlay."""
import hashlib,json,os,re,subprocess,struct
from pathlib import Path
from tools.formats import inspect_pkg
root=Path.cwd();out=root/"local/game/system-metadata";out.mkdir(parents=True,exist_ok=False)
source=(root/"external/LibOrbisPkg/LibOrbisPkg/PKG/Enums.cs").read_text()
enum=source[source.index("public enum EntryId"):]
ids={name:int(value,16) for name,value in re.findall(r"^\s*(\w+)\s*=\s*0x([0-9a-fA-F]+)",enum,re.M)}
names={ids[key]:name for key,name in re.findall(r'\{\s*EntryId\.(\w+),\s*"([^"]+)"\s*\}',source) if key in ids}
for i in range(31):
 names[ids["CHANGEINFO__CHANGEINFO_00_XML"]+i]=f"changeinfo/changeinfo_{i:02}.xml"
for i in range(100):names[ids["TROPHY__TROPHY00_TRP"]+i]=f"trophy/trophy{i:02}.trp"
records={}
for label,pkg in (("base",Path("E:/ROMS/PS4/Bloodborne.pkg")),("update",Path("E:/ROMS/PS4/Bloodborne v1.09 patch.pkg"))):
 for e in inspect_pkg(pkg)["entries"]:
  if not (e["id"]>=0x1000 or e["id"] in (0x402,0x403)):continue
  if e["id"] not in names:raise RuntimeError(f"Unmapped system metadata id {e['id']:x}")
  rel=Path("sce_sys")/names[e["id"]];paths=[];hashes=[]
  for suffix in ("","-repeat"):
   dest=out/(label+suffix)/rel
   if not dest.resolve().is_relative_to(out.resolve()):raise RuntimeError("Unsafe metadata path")
   dest.parent.mkdir(parents=True,exist_ok=True)
   cmd=[str(root/"external/bin/PkgTool/PkgTool.exe"),"pkg_extractentry",str(pkg),str(e["index"]),str(dest)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=30,check=True)
   if "Warning:" in r.stdout or not dest.exists() or dest.stat().st_size!=e["size"]:raise RuntimeError(f"Unverified extraction {e['id']:x}: {r.stdout}")
   data=dest.read_bytes()
   if e["id"]==0x403:
    assert data[:4]==bytes.fromhex("d294a018")
    assert struct.unpack_from(">Q",data,24)[0]>0
   hashes.append(hashlib.sha256(data).hexdigest());paths.append(dest)
  if hashes[0]!=hashes[1]:raise RuntimeError("Repeat differs")
  name=rel.as_posix();prior=records.get(name)
  records[name]=dict(path=name,source=str(paths[0]),sha256=hashes[0],size=e["size"],label=label+"-system-metadata",entry_id=e["id"],package=str(pkg),repeat_verified=True,overrides=prior)
  print(label,name,e["size"],"repeat match",flush=True)
prior=json.loads((root/"local/game/view-manifest.json").read_text())
files=dict(prior["files"])
for name,v in records.items():
 v=dict(v);v["overrides_view"]=files.get(name);files[name]=v
view=root/"local/game/effective-v2";view.mkdir(exist_ok=False)
for name,v in files.items():
 target=view/name
 if not target.resolve().is_relative_to(view.resolve()):raise RuntimeError("Unsafe view path")
 target.parent.mkdir(parents=True,exist_ok=True);os.link(v["source"],target)
summary=dict(schema=2,status="verified",view=str(view),prior_view=str(root/"local/game/effective"),package_sha256=prior["package_sha256"],file_count=len(files),bytes=sum(v["size"] for v in files.values()),system_metadata_files=len(records),system_metadata_repeat_verified=True,game_executable_sha256=files["eboot.bin"]["sha256"])
(out/"manifest.json").write_text(json.dumps(dict(summary=summary,metadata=records),indent=2)+"\n")
(root/"local/game/view-v2-manifest.json").write_text(json.dumps(dict(summary=summary,files=files),indent=2)+"\n")
(root/"reports/input-view-v2.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2),flush=True)
