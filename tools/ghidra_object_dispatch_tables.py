"""Read candidate table bytes and Rela addends independently through Ghidra Java."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('proposals',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
dummy=a.out/'dummy.bin';dummy.write_bytes(b'\0');(a.out/'projects').mkdir();input=(a.proposals/'table-input.json').resolve()
command=[sys.executable,'tools/ghidra_headless.py',str((a.out/'projects').resolve()),'dispatch_tables','-import',str(dummy.resolve()),'-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2','-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckObjectDispatchTables.java',str(input),str((a.out/'tables.json').resolve()),'-log',str((a.out/'application.log').resolve()),'-scriptlog',str((a.out/'script.log').resolve())]
with (a.out/'stdout.log').open('wb') as stdout,(a.out/'stderr.log').open('wb') as stderr:r=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=180)
write_json(a.out/'command.json',dict(argv=command,exit_code=r.returncode));assert r.returncode==0 and (a.out/'tables.json').is_file()
rows=json.loads((a.out/'tables.json').read_text());write_json(a.out/'summary.json',dict(status='independent object table read complete',slots=len(rows),input_sha256=sha(input),output_sha256=sha(a.out/'tables.json'),limitations='Initial slot bytes and little-endian Rela record fields only. Relocation records are not applied to the game, and table/object mutation remains unknown.'))
print(json.dumps(rows),flush=True)
