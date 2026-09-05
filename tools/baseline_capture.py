"""Run a bounded original-code baseline in a fresh, backed-up portable test profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
def write(path,data):
    path.write_bytes((json.dumps(data,indent=2)+"\n").encode("utf-8"))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--id",required=True)
    p.add_argument("--seconds",type=int,default=180)
    p.add_argument("--build",default="shadps4-baseline")
    p.add_argument("--research-capture",action="store_true")
    p.add_argument("--input-script")
    p.add_argument("--axes-script")
    p.add_argument("--game-view",default="local/game/effective-v2")
    p.add_argument("--ime-text")
    p.add_argument("--log-filter")
    p.add_argument("--seed-profile",help="Copy only saved home data and users.json from this project test profile")
    p.add_argument("--tracy-seconds",type=int,default=0)
    a=p.parse_args()
    if not a.id.replace("-","").isalnum() or not 1<=a.seconds<=3600:
        p.error("safe ID and 1-3600 seconds required")
    if a.ime_text and (not a.research_capture or not a.ime_text.isascii() or not a.ime_text.isalnum() or len(a.ime_text)>16):
        p.error("--ime-text requires research capture and 1-16 ASCII letters/digits")
    if not 0<=a.tracy_seconds<a.seconds:
        p.error("Tracy duration must be nonnegative and shorter than the game capture")
    profile=ROOT/"local/profiles"/a.id
    out=ROOT/"local/captures"/a.id
    backup=ROOT/"local/saves/backups"/a.id
    exe=ROOT/"build"/a.build/"shadps4.exe"
    seed=None
    if a.seed_profile:
        seed=(ROOT/"local/profiles"/a.seed_profile).resolve()
        if not seed.is_relative_to((ROOT/"local/profiles").resolve()) or not (seed/"user/home").is_dir():
            p.error("seed must be an existing project test profile")
    if not exe.is_file():p.error("build executable missing")
    profile.mkdir(parents=True,exist_ok=False)
    out.mkdir(parents=True,exist_ok=False)
    backup.mkdir(parents=True,exist_ok=False)
    seed_hashes={}
    if seed:
        shutil.copytree(seed/"user/home",backup/"home")
        shutil.copytree(backup/"home",profile/"user/home")
        if (seed/"user/users.json").exists():
            shutil.copy2(seed/"user/users.json",backup/"users.json")
            shutil.copy2(backup/"users.json",profile/"user/users.json")
        seed_hashes={str(f.relative_to(backup)):digest(f) for f in backup.rglob("*") if f.is_file()}
    for user in range(1000,1004):
        for child in ("savedata","trophy","inputs"):
            (profile/f"user/home/{user}/{child}").mkdir(parents=True,exist_ok=True)
    write(backup/"manifest.json",dict(status="copied_test_save_backup" if seed else "new_empty_profile_no_existing_saves",
                                    profile=str(profile),seed=str(seed) if seed else None,sha256=seed_hashes))
    if a.log_filter:
        write(profile/"user/config.json",{"Log":{"filter":a.log_filter,"flush_level":"info","sync":True}})
    if a.input_script:shutil.copy2(a.input_script,profile/"research-input.tsv")
    if a.axes_script:shutil.copy2(a.axes_script,profile/"research-axes.tsv")
    cmd=[str(exe),"--same-process","-g",str(ROOT/a.game_view/"eboot.bin"),"-f","false"]
    env=os.environ.copy()
    env.pop("BB_RESEARCH_CAPTURE",None);env.pop("BB_RESEARCH_IME_TEXT",None)
    if a.research_capture:env["BB_RESEARCH_CAPTURE"]="1"
    if a.ime_text:env["BB_RESEARCH_IME_TEXT"]=a.ime_text
    write(out/"launch.json",dict(argv=cmd,cwd=str(profile),exe_sha256=digest(exe),
          kind="shadPS4 baseline; original CPU execution",timeout_seconds=a.seconds,
          research_capture=a.research_capture,input_script=a.input_script,ime_text=a.ime_text,
          axes_script=a.axes_script,log_filter=a.log_filter,seed_profile=a.seed_profile,seed_sha256=seed_hashes))
    trace=None;trace_streams=[];trace_result=None
    with (out/"stdout.log").open("wb") as o,(out/"stderr.log").open("wb") as e:
        proc=subprocess.Popen(cmd,cwd=profile,stdout=o,stderr=e,env=env)
        write(out/"pid.json",dict(pid=proc.pid,start=time.time()))
        print(json.dumps(dict(pid=proc.pid,profile=str(profile),capture=str(out))),flush=True)
        try:
            if a.tracy_seconds:
                cap=ROOT/"build/tracy-capture/tracy-capture.exe"
                tcmd=[str(cap),"-a","127.0.0.1","-o",str(out/"profile.tracy"),"-s",str(a.tracy_seconds),"-m","10"]
                write(out/"tracy-launch.json",dict(argv=tcmd,sha256=digest(cap),limit="10 percent physical RAM"))
                trace_streams=[(out/"tracy.stdout").open("wb"),(out/"tracy.stderr").open("wb")]
                trace=subprocess.Popen(tcmd,stdout=trace_streams[0],stderr=trace_streams[1],
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                rc=proc.wait(timeout=a.seconds);reason="process_exit"
            except subprocess.TimeoutExpired:
                proc.terminate();rc=proc.wait(timeout=15);reason="bounded_capture_end"
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
            if trace:
                try:trc=trace.wait(timeout=20);treason="process_exit"
                except subprocess.TimeoutExpired:
                    trace.terminate();trc=trace.wait(timeout=15);treason="capture_timeout"
                trace_result=dict(exit=trc,reason=treason)
                write(out/"tracy-result.json",trace_result)
            for stream in trace_streams:stream.close()
    write(out/"result.json",dict(exit=rc,reason=reason))
    shutil.copytree(profile/"user",out/"profile-after")
    print(json.dumps(dict(exit=rc,reason=reason,tracy=trace_result)),flush=True)
    # A completed bounded capture is not proof that a game checkpoint passed.
    if reason=="process_exit" and rc!=0:return 1
    if trace_result and (trace_result["exit"]!=0 or trace_result["reason"]!="process_exit"):return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
