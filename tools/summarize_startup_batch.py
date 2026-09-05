"""Audit complete startup compilation, retaining rejected entries and runtime boundaries."""
import collections,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();folder=root/'local/compiler-spike/startup-batch-all-v1';source=root/'local/cfg/startup-recovery-v9-repeat'
identity=json.loads((folder/'identity.json').read_text());assert identity['source_manifest_sha256']==sha(source/'compilation-manifest.jsonl') and identity['source_db_sha256']==sha(source/'analysis.sqlite')
units={(u['module_sha256'],u['entry']):u for u in map(json.loads,(source/'compilation-manifest.jsonl').open(encoding='utf-8'))};results=json.loads((folder/'results.json').read_text());bases={r['module']:r['logical_base'] for r in identity['module_mapping']}
quarantined=json.loads((folder/'quarantined-manifests.json').read_text());quarantined_keys={(u['module_sha256'],u['entry']) for u in quarantined};assert len(quarantined)==8 and all(u==units[u['module_sha256'],u['entry']] for u in quarantined)
seen=set();root_owners={};compiled_instructions=set();rejects=[];objects=[];externals=collections.Counter()
for result in results:
 h=result['module'];base=bases[h];p=folder/result['folder'];keys={(h,pc) for pc in result['entries']};assert not seen&keys;seen|=keys
 expected={i['rva']:i['bytes'] for key in keys for i in units[key]['instructions']};data=json.loads((p/'input.json').read_text());assert result['input_sha256']==sha(p/'input.json')
 assert {r['address']-base:r['bytes'] for r in data['instructions']}==expected
 if result['status']=='object_built':
  assert sha(p/'function.obj')==result['object_sha256'];audit=json.loads((p/'audit.json').read_text());assert set(audit['decoded_addresses'])=={base+pc for pc in expected} and not audit['unvisited_manifest_instructions']
  assert set(audit['compiled_roots'])==set(data['roots'])
  nm=subprocess.run([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(p/'function.obj')],capture_output=True,text=True,check=True)
  (p/'symbols-defined.audit.txt').write_text(nm.stdout,encoding='utf-8')
  names={line.split()[0] for line in nm.stdout.splitlines() if line.strip()};assert {f'sub_{pc:x}' for pc in data['roots']}<=names
  for pc in data['roots']:assert pc not in root_owners;root_owners[pc]=result['folder']
  compiled_instructions.update((h,pc) for pc in expected);externals.update(result['external_declarations'])
  objects.append(dict(folder=result['folder'],entries=len(keys),instructions=len(expected),roots=len(data['roots']),object_sha256=result['object_sha256'],symbols_sha256=sha(p/'symbols-defined.audit.txt')))
 else:
  stderr=(p/'lift.stderr').read_text(encoding='utf-8',errors='replace');match=re.search(r'unsupported Remill instruction semantics at (\d+)',stderr);at=int(match[1])-base if match else None
  assert len(keys)==1;key=next(iter(keys));u=units[key]
  rejects.append(dict(module=h,entry=key[1],constructor_ordinal=u['constructor_ordinal'],folder=result['folder'],diagnostic=stderr,site=at,instruction=next((i for i in u['instructions'] if i['rva']==at),None),input_sha256=result['input_sha256']))
assert seen|quarantined_keys==set(units) and not seen&quarantined_keys
summary=json.loads((folder/'summary.json').read_text());assert summary['compiled_units']==21104 and summary['compiled_constructors']==18442 and len(rejects)==48
runs={}
for suffix in ('startup-batch-pilot-v1','startup-batch-all-v1'):
 name='20260905-p3-'+suffix;p=root/'local/runs'/name;m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed' and m['exit_code']==1
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],reason='Complete survey returns failure while any selected entry rejects; all successful and failed outputs retained.',elapsed_seconds=m['elapsed_seconds'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'))
report=dict(status='complete startup compilation census audited; compiler/runtime gates open',directory=folder.relative_to(root).as_posix(),identity=identity,summary=summary,object_count=len(objects),objects=objects,compiled_instruction_addresses=len(compiled_instructions),compiled_logical_roots=len(root_owners),rejected_entries=rejects,quarantined_entries=[dict(module=u['module_sha256'],entry=u['entry'],issues=u['issues']) for u in quarantined],external_declarations=dict(externals),runs=runs,limitations='Every undisputed manifest was attempted. Defined native object symbols and successful semantic lifts are static compilation evidence only. Eight boundary disputes, forty-eight compiler rejections and all unknown indirect/service/callback/exception paths remain. No game objects were linked or executed.',native_game_boot=False,native_port_playable=False)
inspection=root/'local/compiler-spike/startup-rejection-inspection-v1'
if inspection.exists():
 detail=json.loads((inspection/'summary.json').read_text());assert detail['rejected_entries']==48 and detail['decode_failures']==0 and detail['invalid_categories']==0
 report['rejection_inspection']=dict(path=inspection.relative_to(root).as_posix(),summary_sha256=sha(inspection/'summary.json'),problems_sha256=sha(inspection/'problems.json'),summary=detail)
write_json(root/'reports/startup-batch-evidence.json',report)
print(json.dumps(dict(status=report['status'],compiled_units=21104,compiled_constructors=18442,compiled_instruction_addresses=len(compiled_instructions),compiled_logical_roots=len(root_owners),objects=len(objects),rejections=len(rejects),quarantined=8)),flush=True)
