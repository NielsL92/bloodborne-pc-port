import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path.cwd();profile=ROOT/"local/profiles/baseline"
(profile/"user").mkdir(parents=True,exist_ok=True)
research=ROOT/"local/profiles/research";(research/"user").mkdir(parents=True,exist_ok=True)
backups=ROOT/"local/saves/backups/20260905-before-first-launch";backups.mkdir(parents=True,exist_ok=True)
for label,p in (("baseline",profile),("research",research)):
 existing=list((p/"user").rglob("*"))
 if any(f.is_file() for f in existing): raise RuntimeError("Expected a fresh test profile; existing files require a distinct backup run")
(backups/"manifest.json").write_text(json.dumps(dict(status="fresh_profiles_no_existing_saves",profiles=[str(profile),str(research)]),indent=2)+"\n")
exe=ROOT/"build/shadps4-baseline/shadps4.exe"
with exe.open("rb") as f:identity=hashlib.file_digest(f,"sha256").hexdigest()
out=ROOT/"local/captures/baseline-first-boot";out.mkdir(parents=True,exist_ok=True)
cmd=[str(exe),"--same-process","-g",str(ROOT/"local/game/effective/eboot.bin"),"-f","false"]
(out/"launch.json").write_text(json.dumps(dict(argv=cmd,cwd=str(profile),exe_sha256=identity,kind="unmodified shadPS4 baseline; original CPU execution",timeout_seconds=180),indent=2)+"\n")
print(json.dumps(dict(argv=cmd,cwd=str(profile),sha256=identity)),flush=True)
with (out/"stdout.log").open("wb") as o,(out/"stderr.log").open("wb") as e:
 proc=subprocess.Popen(cmd,cwd=profile,stdout=o,stderr=e)
 (out/"pid.json").write_text(json.dumps(dict(pid=proc.pid,start=time.time()))+"\n")
 try:rc=proc.wait(timeout=180);reason="process_exit"
 except subprocess.TimeoutExpired:proc.terminate();rc=proc.wait(timeout=15);reason="bounded_capture_end"
(out/"result.json").write_text(json.dumps(dict(exit=rc,reason=reason),indent=2)+"\n")
print(json.dumps(dict(exit=rc,reason=reason)))
