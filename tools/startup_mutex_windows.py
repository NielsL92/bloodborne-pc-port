"""Prepare independent windows for the first reached constructor and mutex attribute call."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--full-helper',action='store_true');p.add_argument('--ownership',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
h='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9'
windows=[dict(module=h,start=start,end=end) for start,end in [(0x20edf90,0x20ee016),(0x2083fe0,0x2084032),(0x2bbfea8,0x2bbfeb8+6),(0x2bbfec8,0x2bbfed8+6)]]
if a.full_helper:windows[1]['end']=0x20840a6
if a.ownership:windows += [dict(module=h,start=start,end=end) for start,end in [(0x207ee90,0x207eec9),(0x207f070,0x207f0a9),(0x20840b0,0x20840b9),(0x2bbfee8,0x2bbff0e)]]
write_json(a.out/'windows.json',windows);write_json(a.out/'summary.json',dict(status='first constructor and mutex initialization windows prepared',requests_sha256=sha(a.out/'windows.json'),limitations='Windows do not establish function extents or execution coverage. Ghidra receives no expected instructions.'));print('Windows prepared')
