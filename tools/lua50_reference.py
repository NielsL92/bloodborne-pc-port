"""Fetch the publisher-hashed Lua 5.0.2 reference for static source/layout comparison only."""
import argparse,hashlib,io,json,tarfile,urllib.request
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
URL='https://www.lua.org/ftp/lua-5.0.2.tar.gz'
DIGEST='a6c85d85f912e1c321723084389d63dee7660b81b8292452b190ea7190dd73bc'
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--archive',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
if a.archive:data=a.archive.read_bytes()
else:
 with urllib.request.urlopen(URL,timeout=60) as response:data=response.read(1024*1024)
archive=a.out/'lua-5.0.2.tar.gz';archive.write_bytes(data);assert len(data)==190442 and hashlib.sha256(data).hexdigest()==DIGEST
omitted=[]
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
 members=[]
 for item in tar.getmembers():
  dest=(a.out/item.name).resolve();assert dest.is_relative_to(a.out.resolve())
  if item.issym():
   assert (item.name,item.linkname) in [('lua-5.0.2/test/lua','../bin/lua'),('lua-5.0.2/test/luac','../bin/luac')]
   omitted.append(dict(path=item.name,target=item.linkname,reason='Unneeded convenience symlink to an interpreter/compiler executable; all regular source files are retained.'));continue
  assert not item.islnk() and (item.isfile() or item.isdir());members.append(item)
 tar.extractall(a.out,members=members,filter='data')
files={p.relative_to(a.out).as_posix():sha(p) for p in sorted((a.out/'lua-5.0.2').rglob('*')) if p.is_file()}
write_json(a.out/'identity.json',dict(status='publisher-hashed Lua reference downloaded',url=URL,sha256=DIGEST,bytes=len(data),publisher_checksum_url='https://www.lua.org/ftp/',files=files,omitted_convenience_links=omitted,archive_reused_from=str(a.archive) if a.archive else None,purpose='Independent source and static record-layout comparison. No Lua interpreter or guest CPU execution is launched; no native-port runtime is replaced.'))
print(json.dumps(dict(status='reference ready',bytes=len(data),sha256=DIGEST,files=len(files))))
