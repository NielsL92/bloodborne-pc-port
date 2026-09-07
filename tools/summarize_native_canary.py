"""Verify the native libc runtime word, constructor progress and reproducible next stop."""
import argparse,copy,hashlib,json,sqlite3,zipfile
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));base=Path('local/runtime')
def stable(value):
 if isinstance(value,dict):return {k:stable(v) for k,v in value.items() if k not in ('thread','runtime_seed_origin')}
 if isinstance(value,list):return [stable(v) for v in value]
 return value
artifacts={}
for x,y in [('startup-v4-runtime-word','startup-v5-runtime-word-repeat'),('startup-v6-runtime-word-trace','startup-v7-runtime-word-trace-repeat')]:
 one,two=read(base/x/'summary.json'),read(base/y/'summary.json');assert stable(one)==stable(two)
 matched={}
 for path in (base/x).iterdir():
  if path.suffix in ('.obj','.exe','.bin') or path.name in ('probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','native-calls.jsonl','prepare.stdout','entry.stdout'):
   assert sha(path)==sha(base/y/path.name),path;matched[path.name]=sha(path)
 artifacts[y]=matched
one,two=read(base/'canary-v1/summary.json'),read(base/'canary-v2-repeat/summary.json');assert one['objects']==two['objects'];assert one['positive']==two['positive'] and two['positive']['aot_cases']==4096 and two['mismatch_bits']==64
plan=base/'loader-plan-v9-runtime-word';plan_summary=read(plan/'summary.json');providers=read(plan/'native-providers.json');contract=read(base/'canary-contract-v1/contract.json');assert sha(base/'canary-contract-v1/contract.json')==providers['canary']['contract_sha256'];assert plan_summary['unresolved_relocations']==29
for name,digest in plan_summary['files'].items():assert sha(plan/name)==digest
parent=base/'loader-plan-v8-memory';before=[json.loads(s) for s in (parent/'relocations.jsonl').read_text().splitlines()];after=[json.loads(s) for s in (plan/'relocations.jsonl').read_text().splitlines()];changes=[(x,y) for x,y in zip(before,after,strict=True) if x!=y];assert len(changes)==8 and [y for x,y in changes]==providers['canary']['bindings'];assert all(x['value'] is None and x['symbol']['nid']==contract['nid'] and y['value']==contract['logical_address'] for x,y in changes)
for m in read(plan/'modules.json'):assert sha(m['path'])==m['module']
current=read(base/'startup-v7-runtime-word-trace-repeat/summary.json');calls=[json.loads(s) for s in (base/'startup-v7-runtime-word-trace-repeat/native-calls.jsonl').read_text().splitlines()];assert len(calls)==13
atexit=[r for r in calls if r['event']=='import-return' and r['target']==0x102bbe4c8];assert len(atexit)==2 and all(r['rax']==0 for r in atexit)
first=read('local/cfg/startup-v1/roots.json')[0];ctor=0x100000000+first['target'];assert ctor==0x1020edf90 and [r['target'] for r in calls if r['event']=='dispatch']==[0x1000000a0,ctor];assert not any(r['event']=='dispatch-return' and r['target']==ctor for r in calls)
last=calls[-1];assert last['target']==0x102bbfea8 and last['rdi']==0x700000fff48 and last['rsp']==0x700000fff38 and last['memory_operations']==148;assert current['fault']['reason']==25 and current['active_import']['nid']=='F8bUHwAG284'
source=Path('local/cfg/startup-recovery-v31-conditional-repeat');db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);h=first_module='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9';path=db.execute('select path from module where hash=?',(h,)).fetchone()[0];im=ElfImage(Path(path).read_bytes());decoder=Cs(CS_ARCH_X86,CS_MODE_64);checked=[]
for window in read('local/cfg/ghidra-startup-mutex-v1/eboot.bin/ghidra.json'):
 for r in window['instructions']:
  raw=im.at_va(r['rva'],r['length']);assert raw.hex()==r['bytes'];ins=next(decoder.disasm(raw,r['rva'],count=1));assert ins.size==r['length'];old=db.execute('select bytes from recovery_instruction where module=? and rva=?',(h,r['rva'])).fetchone();assert old is None or old[0]==r['bytes'];checked.append(dict(**r,capstone=ins.mnemonic+' '+ins.op_str))
assert len(checked)==59;by={r['rva']:r for r in checked};assert by[0x20ee011]['targets']==[0x2083fe0] and by[0x2084005]['targets']==[0x2bbfea8] and by[0x2083ffe]['bytes']=='4c8d75d8';write_json(a.out/'checked-mutex-instructions.json',checked)
records=[]
for suffix in ['native-canary-scan-v2-gaps','ghidra-canary-reads-v1','native-canary-contract-v1','runtime-canary-v1','runtime-canary-v2-repeat','runtime-word-plan-v1','native-runtime-word-startup-v1','native-runtime-word-startup-v2-repeat','native-runtime-word-startup-v3-trace','native-runtime-word-startup-v4-trace-repeat','startup-mutex-windows-v1','ghidra-startup-mutex-v1','control-v9-trace-regression']:
 folder=Path('local/runs')/('20260907-p4-'+suffix);record=read(folder/'manifest.json');assert record['status']=='pass'
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for rel,digest in record['source_sha256'].items():assert hashlib.sha256(z.read(rel.replace(chr(92),'/'))).hexdigest()==digest
 records.append(dict(run=folder.name,start_utc=record['start_utc'],end_utc=record['end_utc'],manifest_sha256=sha(folder/'manifest.json'),sources_sha256=sha(folder/'sources.zip')))
result=dict(status='native libc runtime word advances startup into the first constructor and reproduces the mutex-attribute stop',current=current,contract=contract,authored_cases=two['positive'],mismatch_bits=64,out_of_bounds_stops=2,reinitialization_rejections=1,changed_relocations=8,remaining_unresolved=29,first_constructor=first,completed_atexit_calls=atexit,trace_events=len(calls),last_call=last,ghidra_instructions=len(checked),identical_artifacts=artifacts,recorders=records,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['The first constructor has entered but not completed. No later constructor or main is claimed.','The diagnostic stream records dispatch/import boundaries, not all statically compiled direct calls or every instruction.','The native seed is recorded for replay. No console seed or complete platform initialization order is inferred.','Five modules have no recovered runtime-word read prefix; unknown widths, mutation and interposition remain explicit.','Twelve other strong data slots and seventeen TLS slots remain guarded. Mutex services, FP/TLS setup, module initialization and helper costs remain open.'])
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],executable_sha256=current['executable_sha256'],executable_bytes=current['executable_bytes'],runtime_seed_sha256=current['runtime_seed_sha256'],first_constructor=hex(ctor),last_call=hex(last['target']),memory_operations=last['memory_operations'])),flush=True)
