"""Final consistency audit; does not rerun the old proof or rehash original PKGs."""
import argparse,ast,collections,hashlib,json,os
p=argparse.ArgumentParser();p.add_argument("--self-run",required=True);a=p.parse_args()
from pathlib import Path
root=Path.cwd()
def read(p):return json.loads((root/p).read_text(encoding="utf-8-sig"))
parsed=0
for folder in ("tools","tests"):
 for p in (root/folder).rglob("*.py"):
  if "__pycache__" in p.parts:continue
  ast.parse(p.read_text(encoding="utf-8-sig"),filename=str(p));parsed+=1
json_files=0
for p in (root/"reports").glob("*.json"):json.loads(p.read_text(encoding="utf-8-sig"));json_files+=1
view=read("local/game/view-v2-manifest.json");files=view["files"];directory=root/"local/game/effective-v2"
assert len(files)==28840
for i,(name,record) in enumerate(files.items(),1):
 target=directory/name;source=Path(record["source"])
 assert target.stat().st_size==record["size"],name
 assert os.path.samefile(target,source),name
 if i%10000==0:print("Checked view links:",i,flush=True)
for package in read("reports/input-manifest.json")["packages"]:
 assert Path(package["path"]).stat().st_size==package["size"]
meta=read("local/game/system-metadata/manifest.json")["metadata"]
for name,record in meta.items():
 with Path(record["source"]).open("rb") as f:sha=hashlib.file_digest(f,"sha256").hexdigest()
 assert sha==record["sha256"] and record["repeat_verified"],name
simd=read("local/compiler-spike/varied-cmpss-fixed/test-summary.json")
graphs=read("local/compiler-spike/graphs-return-count/test-summary.json")
for row in simd+graphs:assert row["exit"]==0 and row["summary"]["failed"]==0
assert sum(r["summary"]["passed"] for r in simd)==4608
assert sum(r["summary"]["passed"] for r in graphs)==6144
assert read("local/compiler-spike/varied-before-cmpss-fix/source-reconstruction.json")["exact"]
scaling=read("local/compiler-spike/scale-default/summary.json")
assert scaling["attempted"]==1000 and scaling["objects_with_unresolved_cpu_boundaries"]==842
assert read("local/compiler-spike/real-jump-v1/summary.json")["passed"]==2112
assert read("local/compiler-spike/real-jump-v1/summary.json")["failed"]==0
assert read("local/compiler-spike/control-flow-v7/summary.json")["nonlocal_callbacks"]==256
assert read("local/compiler-spike/thread-boundary-v2/summary.json")["atomic_pairs"]==8192
assert read("local/cfg/ghidra-bitreader-v1/summary.json")["instruction_boundaries_agree"]==113
assert all(r["exit"]==0 for r in read("local/checks/patch-series-v2/summary.json"))
run_status=collections.Counter();active=[];snapshots=[]
for p in (root/"local/runs").glob("*/manifest.json"):
 value=json.loads(p.read_text(encoding="utf-8-sig"))
 if "status" not in value:
  assert p.parent.name=="final-continuation" and value.get("commit")=="9973e630ebc20375d5fd3f62085cf5438bcda73c" and value.get("clean_worktree"),p
  snapshots.append(dict(path=str(p.relative_to(root)),kind="historical continuation snapshot",commit=value["commit"]))
  continue
 run_status[value["status"]]+=1
 if value["status"]=="running" and p.parent.name!=a.self_run:active.append(p.parent.name)
capture_summary=[]
for p in (root/"local/captures").glob("*/launch.json"):
 result=json.loads((p.parent/"result.json").read_text());assert result["reason"] in ("bounded_capture_end","process_exit")
 images={}
 for image in (p.parent/"profile-after/screenshots").glob("*.png"):
  with image.open("rb") as f:images[image.name]=hashlib.file_digest(f,"sha256").hexdigest()
 (p.parent/"image-hashes.json").write_text(json.dumps(images,indent=2)+"\n",encoding="utf-8")
 capture_summary.append(dict(capture=p.parent.name,result=result,image_count=len(images)))
assert not active,active
result=dict(status="pass",python_sources_parsed=parsed,report_json_files=json_files,verified_effective_links=len(files),metadata_files_rehashed=len(meta),original_packages_rehashed=False,run_status=dict(run_status),active_prior_runs=active,non_command_manifests=snapshots,captures=capture_summary,p2_gate="Bounded feasibility supports P3; broad runtime/game gates remain",native_port_playable=False)
(root/"reports/execution-audit.json").write_bytes((json.dumps(result,indent=2)+"\n").encode("utf-8"))
print(json.dumps(result,indent=2),flush=True)
