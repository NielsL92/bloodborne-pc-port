"""Run one command, preserving argv, source identity, exit, timing and output locally."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--cwd", default=str(ROOT))
    p.add_argument("--timeout", type=int, default=0)
    p.add_argument("command", nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not command or not a.id.replace("-", "").replace("_", "").isalnum():
        p.error("a safe run id and command are required")
    out = ROOT / "local" / "runs" / a.id
    out.mkdir(parents=True, exist_ok=False)
    def git(*args):
        r = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", *args], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    sources = {}
    for directory in ("tools", "native", "tests", "patches"):
        for f in sorted((ROOT / directory).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                sources[str(f.relative_to(ROOT))] = hashlib.sha256(f.read_bytes()).hexdigest()
    with zipfile.ZipFile(out / "sources.zip", "w", zipfile.ZIP_DEFLATED) as snapshot:
        for relative in sources:
            snapshot.write(ROOT / relative, relative)
    manifest = dict(schema=1, argv=command, cwd=str(Path(a.cwd).resolve()),
                    start_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    project_commit=git("rev-parse", "HEAD"), project_status=git("status", "--porcelain"),
                    source_sha256=sources, timeout_seconds=a.timeout or None, status="running")
    mpath = out / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    start = time.monotonic()
    try:
        with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
            result = subprocess.run(command, cwd=a.cwd, stdout=stdout, stderr=stderr,
                                    timeout=a.timeout or None)
        manifest.update(status="pass" if result.returncode == 0 else "failed", exit_code=result.returncode)
    except (OSError, subprocess.TimeoutExpired) as e:
        manifest.update(status="failed", error=str(e), exit_code=None)
    manifest.update(end_utc=dt.datetime.now(dt.timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-start)
    for name in ("stdout.log", "stderr.log"):
        f = out / name
        if f.exists():
            manifest[name + "_sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "source_sha256"}, indent=2))
    raise SystemExit(0 if manifest["status"] == "pass" else 1)

if __name__ == "__main__":
    main()
