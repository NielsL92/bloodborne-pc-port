"""Plan whole-object replacements; never relabel old native objects."""
import collections,json,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike';source=root/'local/cfg/startup-recovery-v22-cache-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=u['instruction_set_sha256']
targets={(r['module'],r['start']) for r in read(base/'x87-selector-inventory-v1/entries.json')};old_batches=['startup-batch-all-v1','startup-fp-recompile-v2-repeat','callback-relocation-compile-v2-repeat','callback-slice-compile-v2-repeat','object-dispatch-compile-v2-repeat','subobject-compile-v2-repeat']
objects=[];owners=collections.defaultdict(list);logical=collections.defaultdict(list)
for name in old_batches:
 folder=base/name
 for result in read(folder/'results.json'):
  if result['status']!='object_built':continue
  artifact=folder/result['folder'];units=read(artifact/'units.json');assert {u['entry'] for u in units}==set(result['entries']) and sha(artifact/'function.obj')==result['object_sha256']
  keys={(result['module'],e) for e in result['entries']};stale=[dict(module=result['module'],entry=u['entry'],compiled_sha256=u['instruction_set_sha256'],current_sha256=current.get((result['module'],u['entry']))) for u in units if current.get((result['module'],u['entry']))!=u['instruction_set_sha256']]
  record=dict(source_batch=name,folder=result['folder'],module=result['module'],entries=result['entries'],compiled_roots=result['compiled_roots'],object_sha256=result['object_sha256'],object_bytes=result['object_bytes'],affected_x87_entries=sorted(e for m,e in keys&targets),stale_units=stale,replace=bool(keys&targets or stale));objects.append(record)
  for key in keys:owners[key].append(record)
  for pc in result['compiled_roots']:logical[pc].append(record)
assert len(objects)==384 and len(owners)==21168 and all(len(v)==1 for v in owners.values())
duplicates=[dict(pc=pc,objects=[r['source_batch']+'/'+r['folder'] for r in group]) for pc,group in logical.items() if len(group)>1];write_json(out/'prior-logical-root-duplicates.json',duplicates)
replacement_keys={key for key,group in owners.items() if group[0]['replace']}|targets;new_keys=replacement_keys-set(owners);assert len(new_keys)==2
selected=[dict(module=m,start=e) for m,e in sorted(replacement_keys)];write_json(out/'entries.json',selected);write_json(out/'prior-objects.json',objects);write_json(out/'replaced-objects.json',[r for r in objects if r['replace']]);write_json(out/'retained-objects.json',[r for r in objects if not r['replace']])
summary=dict(status='whole-object replacement plan retained; no artifacts promoted',prior_objects=len(objects),prior_entries=len(owners),replaced_objects=sum(r['replace'] for r in objects),stale_instruction_sets=sum(len(r['stale_units']) for r in objects),replacement_entries=len(selected),newly_compilable_entries=[dict(module=m,start=e) for m,e in sorted(new_keys)],prior_logical_root_duplicates=len(duplicates),database_sha256=sha(source/'analysis.sqlite'),manifest_sha256=sha(source/'compilation-manifest.jsonl'),entries_sha256=sha(out/'entries.json'),limitations='Includes every entry in each replaced prior object; preserves old files and selected retained objects. Instruction-set hashes are compared against current manifests; counts and static objects do not prove execution or native runtime closure.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True);assert not duplicates
