"""Hash read-only supplied PKGs once; retain exact metadata and stat identity."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from tools.formats import inspect_pkg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/input-manifest.json"

def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def main():
    if OUTPUT.exists():
        raise SystemExit("Manifest exists: reuse recorded hashes; investigate stat changes explicitly.")
    result = {"schema": 1, "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "packages": [], "effective_title_id": "CUSA03173", "effective_app_version": "01.09"}
    for path in [Path("E:/ROMS/PS4/Bloodborne.pkg"), Path("E:/ROMS/PS4/Bloodborne v1.09 patch.pkg")]:
        before = path.stat()
        info = inspect_pkg(path)
        entry = dict(path=str(path), size=before.st_size, mtime_ns=before.st_mtime_ns,
                     sha256=sha(path), sfo=info["sfo"], content_id=info["content_id"])
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError("Input changed while hashing")
        result["packages"].append(entry)
        print(json.dumps(entry), flush=True)
    eboot = ROOT / "local/update/uroot/eboot.bin"
    actual = sha(eboot)
    if actual != "d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9":
        raise RuntimeError("Update executable does not match the handoff")
    result["effective_executable"] = dict(path=str(eboot), sha256=actual, size=eboot.stat().st_size)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
