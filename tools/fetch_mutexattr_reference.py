"""Fetch a primary FreeBSD implementation reference into a fresh recorded directory."""
import argparse,json,urllib.request
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--mutex',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
name='thr_mutex.c' if a.mutex else 'thr_mutexattr.c'
url='https://raw.githubusercontent.com/freebsd/freebsd-src/releng/9.0/lib/libthr/thread/'+name
with urllib.request.urlopen(url,timeout=30) as r:data=r.read()
assert (b'__pthread_mutex_init' in data and b'_pthread_mutex_lock' in data) if a.mutex else (b'_pthread_mutexattr_init' in data and b'_pthread_mutexattr_destroy' in data)
(a.out/name).write_bytes(data);write_json(a.out/'reference.json',dict(url=url,sha256=sha(a.out/name),scope='Independent FreeBSD implementation reference; not a PS4 ABI declaration.'));print('Primary mutex-attribute reference recorded')
