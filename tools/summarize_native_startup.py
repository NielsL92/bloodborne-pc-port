"""Verify the first bounded native entry trace and deterministic portable repeat."""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
base=ROOT/'local/runtime';first=read(base/'startup-v1/summary.json');x=base/'startup-v2-portable';y=base/'startup-v3-repeat';one=read(x/'summary.json');two=read(y/'summary.json')
def stable(value):
 result=copy.deepcopy(value);result['fault'].pop('thread');return result
assert stable(one)==stable(two);assert one['trace_identity']==two['trace_identity']==first['trace_identity'];assert first['fault']['source']==two['fault']['source'] and first['guard']==two['guard']
artifacts={}
for path in x.iterdir():
 if path.suffix in ['.obj','.exe','.bin'] or path.name in ['probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','prepare.stdout','entry.stdout']:
  assert sha(path)==sha(y/path.name),path.name;artifacts[path.name]=sha(path)
records=[]
for suffix in ['startup-entry-windows-v1','ghidra-startup-entry-v1','startup-entry-contract-v1','native-startup-v1','native-startup-v2-portable','native-startup-v3-repeat']:
 folder=ROOT/'local/runs'/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
contract=read(base/'startup-entry-contract-v1/contract.json');assert sha(base/'startup-entry-contract-v1/contract.json')==two['contract_sha256'];assert two['game_aot_execution'] and not two['original_byte_cpu_execution'] and not two['native_game_boot'];assert two['guard']['completed_memory_operations']==11
result=dict(status='first native AOT entry and exact guarded stop reproduced',first_native_entry=records[3],first_probe=first,current=two,contract=contract,identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limits=['The first-entry context is explicitly chosen and bounded; complete startup ABI/initialization order are not established.','Actual supplied entry and libc roots execute only as Remill/LLVM AOT host code. Source byte mappings remain NX and all original inputs are unchanged.','The trace stops before atexit callback registration, constructors and main; it is not a title/graphics/gameplay milestone.','Only the nondeterministic Windows thread ID is excluded from trace equality. Native PE, objects, bundle, preparation data and logical stop fields repeat exactly.','The unresolved __stack_chk_guard slot must receive a separately justified native object binding; the guard has not been bypassed.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=two['executable_sha256'],executable_bytes=two['executable_bytes'],source=two['fault']['source'],address=two['fault']['address'],identical_artifacts=len(artifacts))),flush=True)
