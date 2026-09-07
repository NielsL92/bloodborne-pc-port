"""Prepare independent reader/writer-lock caller windows."""
import argparse
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
h='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9'
windows=[dict(module=h,start=start,end=end) for start,end in [(0x207f2b0,0x207f3a6),(0x207f3d0,0x207f41d),(0x207f640,0x207f68d),(0x207b720,0x207b7dc),(0x2bc0ca8,0x2bc0cae),(0x2bc0cd8,0x2bc0cde),(0x2bc0cf8,0x2bc0cfe),(0x2bc0d28,0x2bc0d2e)]]
write_json(a.out/'windows.json',windows);write_json(a.out/'summary.json',dict(status='reader/writer-lock caller windows prepared',requests_sha256=sha(a.out/'windows.json'),limitations='Independent windows, not function extent or runtime coverage claims.'));print('Windows prepared')
