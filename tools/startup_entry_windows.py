"""Prepare bounded independent checks for the supplied main entry and first libc calls."""
import argparse,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
main='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9';libc='4378b47f46f1d856824a6f971db1a0c3f41833b77f49d2fba9538f667a139166'
windows=[dict(module=main,start=0x20,end=0x91),dict(module=main,start=0xa0,end=0xef),dict(module=main,start=0x2bbe4b8,end=0x2bbe4be),dict(module=main,start=0x2bbe4c8,end=0x2bbe4ce),dict(module=libc,start=0x5fef0,end=0x5fef1),dict(module=libc,start=0x2f110,end=0x2f160)]
write_json(a.out/'windows.json',windows)
registry=Path('local/runtime/registry-v7-memory-repeat');imports=json.loads((registry/'imports.json').read_text(encoding='utf-8'));calls=[next(r for r in imports if r['pc']==pc) for pc in [0x102bbe4b8,0x102bbe4c8]];assert [r['compiled_export'] for r in calls]==[0x80005fef0,0x80002f110];write_json(a.out/'first-imports.json',calls)
write_json(a.out/'summary.json',dict(status='bounded startup entry/import windows prepared',registry_identity_sha256=sha(registry/'identity.json'),windows_sha256=sha(a.out/'windows.json'),game_execution=False,limitations='Windows are analysis requests, not function extent or startup ABI claims. No expected instructions are supplied to Ghidra.'))
print('Startup entry windows prepared',flush=True)
