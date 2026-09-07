"""Prepare independent direct-memory query/allocation/mapping caller windows."""
import argparse
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
h='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9'
windows=[dict(module=h,start=start,end=end) for start,end in [(0x20819f0,0x2081adc),(0x2081e7c,0x2081f05),(0x2bbeaa8,0x2bbeade)]]
write_json(a.out/'windows.json',windows);write_json(a.out/'summary.json',dict(status='direct-memory caller windows prepared',requests_sha256=sha(a.out/'windows.json'),limitations='Independent windows, not function extent or runtime coverage claims.'));print('Windows prepared')
