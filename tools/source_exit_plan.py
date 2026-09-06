"""Carry exact conditional recovery annotations into fresh whole-object inputs."""
import argparse,collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('active',type=Path);p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
active=read(a.active);db=a.source/'analysis.sqlite';db_hash=sha(db);c=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True);contracts={}
for h,entry,source,target_module,target,detail in c.execute("select module,entry,source,target_module,target,detail from recovery_edge where kind='annotated_control_contract_requires_runtime'"):
 size,code,mnemonic=c.execute('select size,bytes,mnemonic from recovery_instruction where module=? and rva=?',(h,source)).fetchone();assert mnemonic=='call' and (h,source) not in contracts
 contracts[h,source]=dict(module=h,entry=entry,source=source,bytes=code,size=size,target_module=target_module,target=target,detail=detail,kind='annotated_control_contract_requires_runtime')
for h,entry,rva in c.execute('select module,entry,rva from recovery_owner'):
 if (h,rva) in contracts:assert contracts[h,rva]['entry']==entry,'conflicting owner scope needs separate compiler inputs'
mapping=None;result=[];covered=set();instance_count=0
for n,obj in enumerate(active):
 old=base/obj['source_batch']/obj['folder'];assert sha(old/'function.obj')==obj['object_sha256'];identity=read(old.parent/'identity.json');current_mapping=identity['module_mapping']
 if mapping is None:mapping=current_mapping
 assert mapping==current_mapping
 bases={m['module']:m['logical_base'] for m in mapping};module=obj['module'];logical_base=bases[module];data=read(old/'input.json');assert not data.get('return_contracts');assert data['roots']==obj['compiled_roots']==read(old/'audit.json')['compiled_roots'];new_contracts=[]
 for ins in data['instructions']:
  key=(module,ins['address']-logical_base)
  if key not in contracts:continue
  row=contracts[key];assert ins['bytes']==row['bytes'] and row['entry'] in obj['entries'];covered.add(key)
  provenance=dict(source_db_sha256=db_hash,**row);new_contracts.append(dict(address=ins['address'],expected_next_pc=ins['address']+row['size'],kind='no-normal-return',provenance=json.dumps(provenance,sort_keys=True,separators=(',',':'))))
 folder=a.out/f'object-{n:04d}';folder.mkdir();data['return_contracts']=sorted(new_contracts,key=lambda r:r['address']);write_json(folder/'input.json',data)
 for name in ['roots.json','units.json']:(folder/name).write_bytes((old/name).read_bytes())
 row=dict(index=n,**obj,prepared_folder=folder.name,input_sha256=sha(folder/'input.json'),roots_sha256=sha(folder/'roots.json'),units_sha256=sha(folder/'units.json'),old_input_sha256=sha(old/'input.json'),instructions=len(data['instructions']),return_contract_count=len(new_contracts),original_missing_instruction_starts=read(old/'audit.json')['missing_instruction_starts']);result.append(row);instance_count+=len(new_contracts)
assert covered==set(contracts),(len(covered),len(contracts))
write_json(a.out/'contracts.json',sorted(contracts.values(),key=lambda r:(r['module'],r['source'])));write_json(a.out/'objects.json',result);write_json(a.out/'identity.json',dict(active_manifest_sha256=sha(a.active),source_db_sha256=db_hash,source_manifest_sha256=sha(a.source/'compilation-manifest.jsonl'),module_mapping=mapping,execution='none; only compiler annotations added to copies of verified input JSON'))
summary=dict(status='all active inputs copied with exact recovery nonreturn provenance',objects=len(result),entries=sum(len(r['entries']) for r in result),compiled_roots=sum(len(r['compiled_roots']) for r in result),instructions=sum(r['instructions'] for r in result),unique_contract_sites=len(contracts),input_contract_instances=instance_count,conflicting_owner_scopes=0,conditional_sites=sum(r['detail'].startswith('disputed-ending-') for r in contracts.values()),source_db_sha256=db_hash,game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
