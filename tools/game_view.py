"""Create a content-hashed, update-precedence local game view. Never modifies PKGs."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from tools.formats import inspect_pkg, read_sfo

ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/"local/game"

def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def metadata(package, label):
    info=inspect_pkg(package)
    sfo=next(e for e in info["entries"] if e["id"]==0x1000)
    assert not sfo["encrypted"]
    with package.open("rb") as f:
        f.seek(sfo["offset"])
        data=f.read(sfo["size"])
    target=GAME/"metadata"/label/"sce_sys/param.sfo"
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if target.read_bytes()!=data:
            raise RuntimeError("Existing metadata differs")
    else:
        target.write_bytes(data)
    return target

def main():
    for run in ("20260905-p0-extract-base-shared","20260905-p0-extract-update-repeat-netsha"):
        m=json.loads((ROOT/"local/runs"/run/"manifest.json").read_text())
        if m["status"]!="pass":
            raise RuntimeError(f"Extraction incomplete: {run}")
    input_manifest=json.loads((ROOT/"reports/input-manifest.json").read_text(encoding="utf-8-sig"))
    records={}
    for label, path in (("base",GAME/"base/uroot"),("update",ROOT/"local/update/uroot")):
        log=GAME/f"{label}-hashes.jsonl"
        cache={}
        if log.exists():
            for line in log.read_text().splitlines():
                v=json.loads(line); cache[v["path"]]=v
        with log.open("a",encoding="utf-8") as out:
            for f in sorted(path.rglob("*")):
                if not f.is_file():
                    continue
                rel=f.relative_to(path).as_posix()
                stat=f.stat()
                v=cache.get(rel)
                if v is None or (v["size"],v["mtime_ns"])!=(stat.st_size,stat.st_mtime_ns):
                    v=dict(path=rel,source=str(f),size=stat.st_size,mtime_ns=stat.st_mtime_ns,sha256=digest(f),label=label)
                    out.write(json.dumps(v)+"\n");out.flush()
                previous=records.get(rel)
                v=dict(v)
                if previous:
                    v["overrides"]=previous
                records[rel]=v
        print(f"{label}: {len(cache)} cached, union now {len(records)} files",flush=True)
    # Independent repeat of update PFS extraction, and previous selective base code.
    repeated=GAME/"update-repeat/uroot"
    expected={p.relative_to(ROOT/"local/update/uroot").as_posix() for p in (ROOT/"local/update/uroot").rglob("*") if p.is_file()}
    actual={p.relative_to(repeated).as_posix() for p in repeated.rglob("*") if p.is_file()}
    if expected!=actual:
        raise RuntimeError(f"Update file sets differ: {expected^actual}")
    for rel in sorted(expected):
        if digest(repeated/rel)!=records[rel]["sha256"]:
            raise RuntimeError(f"Update repeat differs: {rel}")
    selective=ROOT/"local/base-code/uroot"
    for f in selective.rglob("*"):
        if f.is_file() and digest(f)!=digest(GAME/"base/uroot"/f.relative_to(selective)):
            raise RuntimeError(f"Base selective extraction differs: {f.name}")
    for label, pkg in zip(("base","update"),input_manifest["packages"]):
        f=metadata(Path(pkg["path"]),label)
        rel="sce_sys/param.sfo"
        previous=records.get(rel)
        records[rel]=dict(path=rel,source=str(f),size=f.stat().st_size,sha256=digest(f),
                          label=label+"-package-public-metadata",overrides=previous)
    view=GAME/"effective"
    view.mkdir(parents=True,exist_ok=True)
    for rel,v in records.items():
        source=Path(v["source"])
        target=view/rel
        if not target.resolve().is_relative_to(view.resolve()):
            raise RuntimeError("Path escapes view")
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            if not os.path.samefile(source,target):
                raise RuntimeError(f"Existing view entry is not expected hardlink: {rel}")
        else:
            os.link(source,target)
    found={p.relative_to(view).as_posix() for p in view.rglob("*") if p.is_file()}
    if found!=set(records):
        raise RuntimeError("Unexpected files in effective view")
    sfo=read_sfo((view/"sce_sys/param.sfo").read_bytes())
    assert (sfo["TITLE_ID"],sfo["APP_VER"])==("CUSA03173","01.09")
    assert digest(view/"eboot.bin")==input_manifest["effective_executable"]["sha256"]
    result=dict(schema=1,status="verified",kind="hardlinked asset view; do not edit files in place",
                package_sha256=[p["sha256"] for p in input_manifest["packages"]],
                file_count=len(records),bytes=sum(v["size"] for v in records.values()),
                overwrite_count=sum(bool(v.get("overrides")) for v in records.values()),
                repeated_update_files=len(expected), files=records)
    (GAME/"view-manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="files"},indent=2))
if __name__=="__main__":
    main()
