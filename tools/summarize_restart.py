"""Summarize preserved restart evidence and pin current/new tool identities."""
import csv,hashlib,json,math,subprocess,datetime
from pathlib import Path
root=Path.cwd()
def sha(p):
 with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+"\n").encode())
names=["research-finish","research-clinic","research-clinic-reload-continue","research-clinic-movement",
       "research-clinic-sharing-fixed","research-clinic-exit-confirm","research-clinic-proper-exit","research-clinic-clean-reload"]
captures=[]
for name in names:
 p=Path("local/captures")/name;launch=read(p/"launch.json");result=read(p/"result.json")
 log=(p/"profile-after/log/shad_log.txt").read_text(errors="replace")
 images=list((p/"profile-after/screenshots").glob("*.png"))
 captures.append(dict(name=name,result=result,exe_sha256=launch["exe_sha256"],
   sharing_error_32_count=log.count("windows_error=32"),permission_denied_count=log.count("permission denied"),
   screenshot_count=len(images),latest_screenshot=str(sorted(images)[-1]) if images else None,
   log_sha256=sha(p/"profile-after/log/shad_log.txt")))
rows=list(csv.DictReader(Path("local/runs/20260905-p1-tracy-clinic-frames/stdout.log").open()))
times=sorted(int(r["duration_ns"])/1e6 for r in rows if 90e9<=int(r["start_ns"])<130e9)
summary=dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 classification="CPU experiments and instrumented original-code baseline; no native game",
 p2_gate="bounded feasibility supports P3 analysis; broad runtime/game gates remain",
 state_promotion=read("local/compiler-spike/state-promotion-v3/correctness.json"),
 timing=read("local/compiler-spike/state-promotion-v3/measurement/summary.json"),
 control=read("local/compiler-spike/control-flow-v7/summary.json"),
 threads=read("local/compiler-spike/thread-boundary-v2/summary.json"),
 real_jump=read("local/compiler-spike/real-jump-v1/summary.json"),
 file_sharing_probe=read("local/diagnostics/file-sharing-v1/summary.json"),
 captures=captures,
 tracy_diagnostic_interval=dict(start_s=90,end_s=130,frames=len(times),median_ms=times[len(times)//2],
 p95_ms=times[math.ceil(.95*len(times))-1],p99_ms=times[math.ceil(.99*len(times))-1],over_50_ms=sum(x>50 for x in times),
 limitation="heavy trace, screenshot and logging overhead unmeasured; no headline performance comparison"))
write("reports/restart-evidence.json",summary)
lock=read("reports/dependency-lock.json")
# Historical current research binary is preserved under its stable v1 name.
for suffix in ("exe","pdb"):
 old=lock["binaries"].get("build/shadps4-profile/shadps4."+suffix)
 preserved=Path("build/shadps4-profile-capture-v1")/("shadps4."+suffix)
 if old and old["sha256"]=="772b015e0500f86204080f49a5497331f68da2f2091ba1c46c2ccad6ad796491":
  assert sha(preserved)==old["sha256"]
paths=[]
for d in ("shadps4-profile-capture-v1","shadps4-profile-ime-v1","shadps4-profile-diagnostics-v1","shadps4-profile"):
 for suffix in ("exe","pdb"):paths.append(Path("build")/d/("shadps4."+suffix))
paths += [Path("build/tracy-capture")/n for n in ("tracy-capture.exe","tracy-csvexport.exe","bb-tracy-frames.exe")]
paths += [Path("build/state-promotion/bb-state-promotion.exe")]
for p in paths:lock["binaries"][p.as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
for p in Path("patches").glob("*.patch"):lock["patches"][p.name]=sha(p)
def git(path,*args):return subprocess.check_output(["git","-c",f"safe.directory={path.resolve().as_posix()}","-C",str(path),*args],text=True).strip()
tracy=Path("external/tracy-tools")
lock["repositories"]["tracy-tools"]=dict(commit=git(tracy,"rev-parse","HEAD"),origin=git(tracy,"remote","get-url","origin"),version="0.11.1",protocol=69)
lock["tracy_dependency_sources"]=[]
for p in sorted(Path("build/tracy-capture/_deps").glob("*-src")):
 lock["tracy_dependency_sources"].append(dict(path=p.as_posix(),commit=git(p,"rev-parse","HEAD"),origin=git(p,"remote","get-url","origin")))
lock["shad_research_patch_order"]=["shadps4-research-capture.patch","shadps4-research-ime.patch","shadps4-research-diagnostics.patch","shadps4-guest-file-sharing.patch"]
lock["recorded_utc"]=summary["recorded_utc"]
write("reports/dependency-lock.json",lock)
print(json.dumps(dict(captures=[dict(name=x["name"],sharing32=x["sharing_error_32_count"],denied=x["permission_denied_count"]) for x in captures],binaries_hashed=len(paths))))
