"""Copy the complete active startup inputs and explicitly select native source bridges."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('active',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
base=Path('local/compiler-spike');rows=[];identity=None
for n,obj in enumerate(read(a.active)):
 old=base/obj['source_batch']/obj['folder'];assert sha(old/'function.obj')==obj['object_sha256'];prior=read(old.parent/'identity.json')
 if identity is None:identity=prior
 assert prior==identity
 data=read(old/'input.json');audit=read(old/'audit.json');assert not data.get('native_memory_provenance');assert data['roots']==obj['compiled_roots']==audit['compiled_roots'];assert not audit['unvisited_manifest_instructions'];assert set(audit['decoded_addresses'])=={i['address'] for i in data['instructions']}
 data['native_memory_provenance']=True;folder=a.out/f'object-{n:04d}';folder.mkdir();write_json(folder/'input.json',data)
 for name in ['roots.json','units.json']:(folder/name).write_bytes((old/name).read_bytes())
 rows.append(dict(index=n,**obj,prepared_folder=folder.name,input_sha256=sha(folder/'input.json'),roots_sha256=sha(folder/'roots.json'),units_sha256=sha(folder/'units.json'),old_input_sha256=sha(old/'input.json'),instructions=len(data['instructions']),return_contract_count=len(data['return_contracts']),original_missing_instruction_starts=audit['missing_instruction_starts']))
assert len(rows)==386 and sum(r['instructions'] for r in rows)==874279
identity=dict(active_manifest_sha256=sha(a.active),source_db_sha256=identity['source_db_sha256'],source_manifest_sha256=identity['source_manifest_sha256'],module_mapping=identity['module_mapping'],native_memory_provenance=True,execution='none; exact existing inputs copied with explicit native helper ABI selection')
write_json(a.out/'objects.json',rows);write_json(a.out/'identity.json',identity);summary=dict(status='complete startup inputs prepared with native instruction-source ABI',objects=len(rows),instructions=sum(r['instructions'] for r in rows),game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
