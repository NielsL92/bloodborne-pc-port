"""Allocate canonical logical identities for unresolved external function imports."""
import argparse,collections,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('registry',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
modules=read(a.registry/'modules.json');links={};exports=collections.defaultdict(list)
def key(link,symbol,defined):
 libraries=link['export_libraries' if defined else 'libraries'];module_info=link['export_modules' if defined else 'modules'];libs=[r for r in libraries if r['name']==symbol['library']];mods=[r for r in module_info if r['name']==symbol['module']]
 assert len(libs)==len(mods)==1,('nonunique import namespace',symbol);return symbol['nid'],symbol['library'],libs[0]['version'],symbol['module'],mods[0]['version']
for module in modules:
 h=module['module'];assert sha(module['path'])==h;link=links[h]=ElfImage(Path(module['path']).read_bytes()).linkage()
 for s in link['symbols']:
  if s['defined'] and s['type']==2 and s['library'] is not None:exports[key(link,s,True)].append(dict(module=h,pc=module['logical_base']+s['value']))
services=collections.defaultdict(list);bundled=[]
for module in modules:
 h=module['module'];link=links[h];referenced=collections.defaultdict(list)
 for rel in link['relocations']:referenced[rel['symbol']].append(rel)
 for s in link['symbols']:
  if s['defined'] or s['type']!=2 or not referenced[s['index']]:continue
  assert s['bind']==1,'weak function requires independent resolution';identity=key(link,s,False);candidates=exports.get(identity,[]);assert len(candidates)<=1,('ambiguous native/bundled import',identity)
  use=dict(module=h,name=module['name'],symbol_index=s['index'],symbol_name=s['name'],relocations=referenced[s['index']])
  if candidates:bundled.append(dict(identity=identity,use=use,target=candidates[0]));continue
  services[identity].append(use)
base=0x900000000;limit=0xa00000000;assert all(not (base<=m['logical_base']<limit) for m in modules)
rows=[]
for index,(identity,uses) in enumerate(sorted(services.items())):
 nid,library,library_version,module,module_version=identity;rows.append(dict(pc=base+16*index,nid=nid,library=library,library_version=library_version,module=module,module_version=module_version,uses=uses,native_implementation='unimplemented explicit stop',game_code=False))
assert rows and rows[-1]['pc']<limit;write_json(a.out/'native-services.json',rows);write_json(a.out/'bundled-imports.json',bundled)
summary=dict(status='canonical external-function identity manifest generated',source_registry_identity_sha256=sha(a.registry/'identity.json'),reserved_logical_range=[base,limit],services=len(rows),import_symbol_uses=sum(len(r['uses']) for r in rows),relocation_uses=sum(len(u['relocations']) for r in rows for u in r['uses']),cross_module_services=sum(len({u['module'] for u in r['uses']})>1 for r in rows),bundled_import_symbols=len(bundled),services_sha256=sha(a.out/'native-services.json'),bundled_sha256=sha(a.out/'bundled-imports.json'),game_execution=False,limitations='Canonical native logical addresses are one per exact NID/library/module/version identity. This reserves module slot 9 for native service identifiers, with no original bytes or executable data mapping. Real service behavior and pointer use in game execution remain unvalidated.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
