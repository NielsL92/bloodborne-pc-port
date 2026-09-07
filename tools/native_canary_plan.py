"""Add the validated libc runtime word to a fresh loader plan; retain every other unknown."""
import argparse,collections,json,shutil
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('contract',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
old=Path('local/runtime/loader-plan-v8-memory');summary=read(old/'summary.json');contract=read(a.contract/'contract.json');assert summary['registry_identity_sha256']==read(Path('local/runtime/canary-scan-v2-gaps/summary.json'))['registry_identity'];checks=read(Path('local/runtime/canary-v1/summary.json'));assert checks['positive']['aot_cases']==4096 and checks['mismatch_bits']==64
for name,digest in summary['files'].items():assert sha(old/name)==digest;shutil.copyfile(old/name,a.out/name)
uses={(r['module'],r['relocation']['offset']):r for r in contract['uses']};rows=[];bound=[]
for r in map(json.loads,(old/'relocations.jsonl').read_text(encoding='utf-8').splitlines()):
 key=r['module'],r['offset']
 if key in uses:
  assert r==uses[key]['relocation'];r=dict(r,value=contract['logical_address'],kind='native process runtime word',provider_contract_sha256=sha(a.contract/'contract.json'));bound.append(r)
 rows.append(r)
assert len(bound)==8
regions=read(old/'regions.json');assert not any(r['base']<contract['logical_address']+8 and contract['logical_address']<r['base']+r['mapped_size'] for r in regions)
file='native-runtime-word.bin';(a.out/file).write_bytes(bytes(8));regions.append(dict(module=None,native_provider='libkernel:f7uOxY9mM1U',base=contract['logical_address'],mapped_size=8,declared_memory_size=8,file_size=8,zero_tail=0,native_rights=contract['rights'],initial_file=file,initial_sha256=sha(a.out/file),guest_executable=False,requires_native_initialization=True))
write_json(a.out/'regions.json',regions);write_json(a.out/'unresolved-relocations.json',[r for r in rows if r['value'] is None]);(a.out/'relocations.jsonl').write_text(chr(10).join(json.dumps(r,separators=(',',':')) for r in rows)+chr(10),encoding='utf-8');write_json(a.out/'native-providers.json',dict(canary=dict(contract_sha256=sha(a.contract/'contract.json'),logical_address=contract['logical_address'],size=8,rights=contract['rights'],requires_initialization_before_entry=True,nid=contract['nid'],library=contract['library'],library_version=contract['library_version'],module=contract['module'],module_version=contract['module_version'],bindings=bound)))
summary.update(status='loader plan includes native-initialized libc runtime word',regions=len(regions),mapped_bytes=summary['mapped_bytes']+8,initial_bytes=summary['initial_bytes']+8,unresolved_relocations=sum(r['value'] is None for r in rows),classification=dict(collections.Counter(r['kind'] for r in rows)),parent_plan_sha256=sha(old/'summary.json'),native_provider_contract_sha256=sha(a.contract/'contract.json'),native_initialization_required=True)
summary['files']={path.name:sha(path) for path in sorted(a.out.iterdir()) if path.is_file()};summary['limitations']+=['The native runtime word is storage only until native initialization; entry is prohibited before that step.','One exact namespace/version identity is shared across eight imports. Five cold-module read prefixes remain unobserved in the current recovered set.'];write_json(a.out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],bound_runtime_slots=8,remaining_unresolved=summary['unresolved_relocations'])),flush=True)
