"""Fetch the fixed public SoftFloat 3e source release without executing it."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();url='https://www.jhauser.us/arithmetic/SoftFloat-3e.zip';archive=root/'external/downloads/SoftFloat-3e.zip';target=root/'external/SoftFloat-3e'
assert not archive.exists() and not target.exists()
archive.parent.mkdir(parents=True,exist_ok=True)
with urllib.request.urlopen(url,timeout=60) as response:
 data=response.read(2_000_001)
 assert len(data)<2_000_000
assert hashlib.sha256(data).hexdigest()=='21130ce885d35c1fe73fc1e1bf2244178167e05c6747cad5f450cc991714c746', 'fixed release identity changed'
archive.write_bytes(data)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in z.infolist():
  p=Path(row.filename)
  assert p.parts[0]=='SoftFloat-3e' and not p.is_absolute() and '..' not in p.parts
 z.extractall(root/'external')
assert (target/'COPYING.txt').is_file()
record=dict(status='public source archive fetched and integrity checked; no library code executed',url=url,bytes=len(data),sha256=sha(archive),archive=str(archive),source=str(target),license_sha256=sha(target/'COPYING.txt'),files={p.relative_to(target).as_posix():sha(p) for p in sorted(target.rglob('*')) if p.is_file()},hash_note='Pinned to the locally recorded identity of the HTTPS release archive; this is not a separately published publisher checksum.')
write_json(root/'reports/softfloat-source.json',record);print(json.dumps({k:v for k,v in record.items() if k!='files'}),flush=True)
