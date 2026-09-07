"""Fetch a primary FreeBSD implementation reference into a fresh recorded directory."""
import argparse,json,urllib.request
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
url='https://raw.githubusercontent.com/freebsd/freebsd-src/releng/9.0/lib/libthr/thread/thr_mutexattr.c'
with urllib.request.urlopen(url,timeout=30) as r:data=r.read()
assert b'_pthread_mutexattr_init' in data and b'_pthread_mutexattr_destroy' in data
(a.out/'thr_mutexattr.c').write_bytes(data);write_json(a.out/'reference.json',dict(url=url,sha256=sha(a.out/'thr_mutexattr.c'),scope='Independent FreeBSD implementation reference; not a PS4 ABI declaration.'));print('Primary mutex-attribute reference recorded')
