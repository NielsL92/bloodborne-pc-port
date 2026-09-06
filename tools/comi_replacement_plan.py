"""Select every complete retained object containing a recovered COMI/UCOMI site."""
import collections,json,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
source=Path(sys.argv[1]).resolve();manifest=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve();out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike').resolve()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
db=sqlite3.connect((source/'analysis.sqlite').as_uri()+'?mode=ro',uri=True)
ops=['comiss','comisd','ucomiss','ucomisd','vcomiss','vcomisd','vucomiss','vucomisd'];sites=[dict(module=m,rva=r,mnemonic=n,bytes=b) for m,r,n,b in db.execute('SELECT module,rva,mnemonic,bytes FROM recovery_instruction WHERE mnemonic IN ('+','.join('?' for _ in ops)+') ORDER BY module,rva',ops)]
lookup={(s['module'],s['rva']):s for s in sites};selected=[];retained=[];covered=collections.Counter();identities={};owners=set()
for index,obj in enumerate(read(manifest)):
 folder=base/obj['source_batch']/obj['folder'];assert sha(folder/'function.obj')==obj['object_sha256'];identity=identities.setdefault(obj['source_batch'],read(folder.parent/'identity.json'));bases={m['module']:m['logical_base'] for m in identity['module_mapping']};data=read(folder/'input.json');assert data['roots']==obj['compiled_roots'];hits=[]
 for ins in data['instructions']:
  key=(obj['module'],ins['address']-bases[obj['module']])
  if key in lookup:
   assert ins['bytes']==lookup[key]['bytes'];covered[key]+=1;hits.append(lookup[key])
 row=dict(index=index,**obj)
 if hits:
  row.update(sites=hits,input_sha256=sha(folder/'input.json'),units_sha256=sha(folder/'units.json'),roots_sha256=sha(folder/'roots.json'));selected.append(row);owners.update((obj['module'],e) for e in obj['entries'])
 else:retained.append(row)
assert set(covered)==set(lookup) and len(sites)==49
write_json(out/'sites.json',sites);write_json(out/'selected-objects.json',selected);write_json(out/'retained-objects.json',retained)
write_json(out/'summary.json',dict(status='exact complete-object replacement plan; no input execution',source_manifest_sha256=sha(source/'compilation-manifest.jsonl'),active_manifest=str(manifest),active_manifest_sha256=sha(manifest),sites=len(sites),site_counts=dict(collections.Counter(s['mnemonic'] for s in sites)),affected_objects=len(selected),affected_entries=len(owners),retained_objects=len(retained),site_object_occurrences=sum(covered.values()),artifact_sha256={n:sha(out/n) for n in ['sites.json','selected-objects.json','retained-objects.json']}));print(json.dumps(read(out/'summary.json')),flush=True)
