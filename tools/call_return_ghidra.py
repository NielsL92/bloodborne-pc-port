"""Independent SLEIGH boundary check of the disputed authored CALL/POP idiom."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();blob=out/'authored.bin';blob.write_bytes(bytes.fromhex('e80000000058c3'));dummy=out/'dummy.bin';dummy.write_bytes(b'\0');(out/'projects').mkdir();pc=0x100092000
write_json(out/'input.json',dict(segments=[dict(name='authored_call_pop',rva=pc,path=str(blob))],entries=[dict(start=pc,end=pc+7)]))
argv=[sys.executable,'tools/ghidra_headless.py',str(out/'projects'),'call_pop','-import',str(dummy),'-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2','-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckRecovery.java',str(out/'input.json'),str(out/'ghidra.json'),'-log',str(out/'application.log'),'-scriptlog',str(out/'script.log')]
with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=180)
assert r.returncode==0
result=json.loads((out/'ghidra.json').read_text(encoding='utf-8'));rows=result[0]['instructions'];assert [(i['rva'],i['length'],i['bytes']) for i in rows]==[(pc,5,'e800000000'),(pc+5,1,'58'),(pc+6,1,'c3')]
summary=dict(status='independent CALL/POP instruction boundaries agree',instructions=rows,input_sha256=sha(blob),ghidra_sha256=sha(out/'ghidra.json'),game_execution=False,scope='Authored seven-byte window, no expected instruction starts or function hints supplied to Ghidra.');write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
