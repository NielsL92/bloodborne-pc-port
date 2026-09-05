"""Download pinned public build tools locally, verifying official release digests."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = [
    ("llvm-21.1.8.tar.xz", "https://github.com/llvm/llvm-project/releases/download/llvmorg-21.1.8/clang%2Bllvm-21.1.8-x86_64-pc-windows-msvc.tar.xz", "749d22f565fcd5718dbed06512572d0e5353b502c03fe1f7f17ee8b8aca21a47"),
    ("cmake-4.2.3.zip", "https://github.com/Kitware/CMake/releases/download/v4.2.3/cmake-4.2.3-windows-x86_64.zip", "eb4ebf5155dbb05436d675706b2a08189430df58904257ae5e91bcba4c86933c"),
    ("ninja-1.13.2.zip", "https://github.com/ninja-build/ninja/releases/download/v1.13.2/ninja-win.zip", "07fc8261b42b20e71d1720b39068c2e14ffcee6396b76fb7a795fb460b78dc65"),
]
def acquire(asset):
    name, url, digest = asset
    dest = ROOT / "external/downloads" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        partial = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, partial)
        with partial.open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        if actual != digest:
            raise RuntimeError(f"{name}: SHA256 mismatch")
        partial.rename(dest)
    with dest.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != digest:
            raise RuntimeError(f"{name}: cached SHA256 mismatch")
    out = ROOT / "external/toolchains" / name.split(".tar")[0].removesuffix(".zip")
    marker = out / ".verified-extraction"
    if not marker.exists():
        out.mkdir(parents=True, exist_ok=True)
        if name.endswith(".zip"):
            with zipfile.ZipFile(dest) as z:
                for item in z.infolist():
                    target = (out / item.filename).resolve()
                    if not target.is_relative_to(out.resolve()):
                        raise RuntimeError("Archive path escapes output")
                z.extractall(out)
        else:
            with tarfile.open(dest, "r:xz") as t:
                t.extractall(out, filter="data")
        marker.write_text(digest + "\n")
    print(f"verified {name}: {out}", flush=True)
    return dict(archive=name, url=url, sha256=digest, directory=str(out))

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(acquire, ASSETS))
    (ROOT / "reports/toolchain-downloads.json").write_text(json.dumps(records, indent=2)+"\n")
