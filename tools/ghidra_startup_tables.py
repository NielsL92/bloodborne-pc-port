"""Independent Ghidra table evidence for two library startup decode disputes."""
import json,sqlite3,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect('file:local/cfg/startup-recovery-v3/analysis.sqlite?mode=ro',uri=True)
h,path=db.execute("SELECT hash,path FROM module WHERE name='libc.prx'").fetchone();assert sha(path)==h
im=ElfImage(Path(path).read_bytes());segments=[]
for n,s in enumerate(im.segments):
 if s.type not in (1,0x61000010) or not s.filesz:continue
 target=out/f'segment-{n}.bin';target.write_bytes(im.file_bytes(s.offset,s.filesz));segments.append(dict(name=f'mapped_{n}',rva=s.vaddr,path=str(target.resolve())))
write_json(out/'input.json',dict(module_sha256=h,segments=segments,abort_rva=0x1f560,abort_contract='tools/cfg_import_contracts.json exact hash/RVA/bytes; ABI no-return only',entries=[0x61370,0x61640]))
(out/'dummy.bin').write_bytes(b'\0');(out/'projects').mkdir()
cmd=[sys.executable,'tools/ghidra_headless.py',str((out/'projects').resolve()),'switches','-import',str((out/'dummy.bin').resolve()),'-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2','-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckStartupTables.java',str((out/'input.json').resolve()),str(out.resolve()),'-log',str((out/'application.log').resolve()),'-scriptlog',str((out/'script.log').resolve())]
with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:r=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=600)
if r.returncode or not (out/'ghidra.json').exists():raise RuntimeError('Ghidra switch recovery failed; retained logs')
actual=json.loads((out/'ghidra.json').read_text());summary=dict(status='independent static switch candidates; not execution coverage',module_sha256=h,functions=[dict(entry=r['entry'],tables=r['tables'],instructions=len(r['instructions'])) for r in actual],ghidra_sha256=sha(out/'ghidra.json'),limitations='Ghidra received raw mapped bytes and the verified abort API contract. No switch targets or table contents were supplied as annotations. Bounds/bytes still require a separate comparison; no native exception execution.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
