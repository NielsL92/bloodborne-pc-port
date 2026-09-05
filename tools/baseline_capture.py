"""Bounded unmodified baseline capture with a new isolated portable profile."""
import argparse,hashlib,json,subprocess,time,shutil,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--id",required=True);p.add_argument("--seconds",type=int,default=180);p.add_argument("--build",default="shadps4-baseline");p.add_argument("--research-capture",action="store_true");p.add_argument("--input-script");p.add_argument("--game-view",default="local/game/effective")
a=p.parse_args()
if not a.id.replace("-","").isalnum():p.error("safe id required")
root=Path.cwd();profile=root/"local/profiles"/a.id;out=root/"local/captures"/a.id
profile.mkdir(parents=True,exist_ok=False);out.mkdir(parents=True,exist_ok=False)
# UserManager::CreateDefaultUsers prompts migration only if home/1000 is absent.
# These directories contain no imported or preexisting saves.
for user in range(1000,1004):
 for child in ("savedata","trophy","inputs"):(profile/f"user/home/{user}/{child}").mkdir(parents=True)
backup=root/"local/saves/backups"/a.id;backup.mkdir(parents=True,exist_ok=False)
(backup/"manifest.json").write_text(json.dumps(dict(status="new_empty_profile_no_existing_saves",profile=str(profile)),indent=2)+"\n")
if a.input_script:shutil.copy2(a.input_script,profile/"research-input.tsv")
exe=root/"build"/a.build/"shadps4.exe"
with exe.open("rb") as f:identity=hashlib.file_digest(f,"sha256").hexdigest()
cmd=[str(exe),"--same-process","-g",str(root/a.game_view/"eboot.bin"),"-f","false"]
(out/"launch.json").write_text(json.dumps(dict(argv=cmd,cwd=str(profile),exe_sha256=identity,kind="shadPS4 baseline; original CPU execution",timeout_seconds=a.seconds,research_capture=a.research_capture,input_script=a.input_script,profile_setup="empty portable home directories, users 1000-1003"),indent=2)+"\n")
with (out/"stdout.log").open("wb") as o,(out/"stderr.log").open("wb") as e:
 env=os.environ.copy()
 if a.research_capture:env["BB_RESEARCH_CAPTURE"]="1"
 proc=subprocess.Popen(cmd,cwd=profile,stdout=o,stderr=e,env=env)
 (out/"pid.json").write_text(json.dumps(dict(pid=proc.pid,start=time.time()))+"\n")
 print(json.dumps(dict(pid=proc.pid,profile=str(profile),capture=str(out))),flush=True)
 try:rc=proc.wait(timeout=a.seconds);reason="process_exit"
 except subprocess.TimeoutExpired:proc.terminate();rc=proc.wait(timeout=15);reason="bounded_capture_end"
(out/"result.json").write_text(json.dumps(dict(exit=rc,reason=reason),indent=2)+"\n")
shutil.copytree(profile/"user",out/"profile-after")
print(json.dumps(dict(exit=rc,reason=reason)),flush=True)
# A successful capture is not a successful game boot; inspect the preserved log.
