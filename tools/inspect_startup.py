"""Read-only inspection of the preserved P3 startup checkpoint."""
import bisect, collections, hashlib, json, sqlite3
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from tools.formats import ElfImage

root = Path.cwd()
source = root / 'local/cfg/startup-db-v1'
db = sqlite3.connect(f'{(source / "analysis.sqlite").as_uri()}?mode=ro', uri=True)
assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
frontier = json.loads((source / 'frontier.json').read_text())
traversed = json.loads((source / 'traversed.json').read_text())
roots = json.loads((root / 'local/cfg/startup-v1/roots.json').read_text())
h, path = db.execute("SELECT hash,path FROM module WHERE name='eboot.bin'").fetchone()
raw = Path(path).read_bytes()
assert hashlib.sha256(raw).hexdigest() == h
im = ElfImage(raw)
ranges = db.execute('SELECT start,size FROM unwind_range WHERE module=? ORDER BY start', (h,)).fetchall()
starts = [r[0] for r in ranges]
contain = collections.Counter()
for r in roots:
    index = bisect.bisect_right(starts, r['target']) - 1
    a, size = ranges[index] if index >= 0 else (-1, 0)
    contain['indexed_start' if a == r['target'] else 'indexed_interior' if a <= r['target'] < a + size else 'outside_indexed_ranges'] += 1
print(json.dumps(dict(db_sha256=hashlib.sha256((source/'analysis.sqlite').read_bytes()).hexdigest(),
    frontier=dict(collections.Counter(r['kind'] for r in frontier)), traversed=traversed,
    constructor_count=len(roots), containment=dict(contain),
    schemas=db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name LIKE 'exception%' ").fetchall()), indent=2))
decoder = Cs(CS_ARCH_X86, CS_MODE_64)
for r in roots[:4] + [r for r in roots if not r['indexed_unwind_start']][::4000]:
    print(json.dumps(r))
    for i in decoder.disasm(im.at_va(r['target'], 128), r['target']):
        print(f'{i.address:x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
        if i.mnemonic in ('ret', 'jmp'): break
db.close()
