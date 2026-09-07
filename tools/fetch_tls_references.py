"""Record primary FreeBSD TLS layout and implementation references."""
import argparse,urllib.request
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);records=[]
for name,relative in [('rtld.c','libexec/rtld-elf/rtld.c'),('reloc.c','libexec/rtld-elf/amd64/reloc.c'),('pthread_md.h','lib/libthr/arch/amd64/include/pthread_md.h')]:
 url='https://raw.githubusercontent.com/freebsd/freebsd-src/releng/9.0/'+relative
 with urllib.request.urlopen(url,timeout=30) as r:data=r.read()
 assert len(data)>1000 and b'Copyright' in data;(a.out/name).write_bytes(data);records.append(dict(path=name,url=url,sha256=sha(a.out/name)))
write_json(a.out/'references.json',dict(records=records,scope='Independent FreeBSD TLS references; not complete PS4 ABI or console observations.'));print('Primary TLS references recorded')
