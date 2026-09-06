"""Run independent Ghidra symbol/Rela dispatch inspection."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
dummy=a.out/'dummy.bin';dummy.write_bytes(b'\0');(a.out/'projects').mkdir();input=(a.proposal/'symbol-input.json').resolve()
cmd=[sys.executable,'tools/ghidra_headless.py',str((a.out/'projects').resolve()),'symbol_dispatch','-import',str(dummy.resolve()),'-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2','-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckSymbolDispatch.java',str(input),str((a.out/'dispatch.json').resolve()),'-log',str((a.out/'application.log').resolve()),'-scriptlog',str((a.out/'script.log').resolve())]
with (a.out/'stdout.log').open('wb') as out,(a.out/'stderr.log').open('wb') as err:r=subprocess.run(cmd,stdout=out,stderr=err,timeout=180)
write_json(a.out/'command.json',dict(argv=cmd,exit_code=r.returncode));assert r.returncode==0 and (a.out/'dispatch.json').exists()
write_json(a.out/'summary.json',dict(status='independent symbol dispatch read complete',input_sha256=sha(input),output_sha256=sha(a.out/'dispatch.json'),script_sha256=sha('tools/ghidra_scripts/BBCheckSymbolDispatch.java'),limitations='Supplied initial bytes and symbol/Rela metadata only. No runtime binding, immutability or game execution claim.'))
print((a.out/'dispatch.json').read_text(encoding='utf-8'))
