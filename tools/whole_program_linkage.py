"""Read actual COFF symbols and explicit exits across a complete active object set.

This is a static linkage inventory. No linker, game entry, original code, or
service stub is executed. A target existing in the map never authorizes dispatch.
"""
import argparse,collections,concurrent.futures,json,re,sqlite3,subprocess
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_JUMP
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
from tools.formats import ElfImage

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('manifest',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);root=Path.cwd();base=root/'local/compiler-spike';nm=LLVM/'bin/llvm-nm.exe'
 def read(p):return json.loads(p.read_text(encoding='utf-8'))
 active=read(a.manifest);db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 modules=sorted(db.execute('SELECT hash,name,path FROM module'),key=lambda r:(r[1]!='eboot.bin',r[1]));mapping=[dict(module=h,name=name,logical_base=(n+1)*0x100000000) for n,(h,name,path) in enumerate(modules)];slot={x['logical_base']:x for x in mapping};bases={x['module']:x['logical_base'] for x in mapping}
 for batch in sorted({x['source_batch'] for x in active}):assert read(base/batch/'identity.json')['module_mapping']==mapping,'retained logical module mapping differs'
 known_roots={pc for obj in active for pc in obj['compiled_roots']};assert len(known_roots)==sum(len(obj['compiled_roots']) for obj in active)
 contexts={};flow_decoder=Cs(CS_ARCH_X86,CS_MODE_64);flow_decoder.detail=True
 # Per-object units.json contains identities, not bodies. Read current source
 # manifests once and keep only compact edge context after checking identities.
 for line in (a.source/'compilation-manifest.jsonl').open(encoding='utf-8'):
  u=json.loads(line);ins={i['rva']:i for i in u['instructions']};after=collections.defaultdict(list);transfers=collections.defaultdict(list)
  for e in u['edges']:
   if e['kind']=='annotated_control_contract_requires_runtime':
    i=ins[e['source']];after[e['source']+i['size']].append(dict(entry=u['entry'],source=e['source'],contract=e['detail'],instruction_bytes=i['bytes']))
   if e['target_module']==u['module_sha256'] and e['kind'] in ('cross_fence_jump','direct_jump','validated_jump_table','independently_recovered_jump_table'):
    transfers[e['target']].append(dict(entry=u['entry'],source=e['source'],kind=e['kind']))
   if e['kind']=='import_contract_unvalidated':
    i=ins[e['source']];decoded=next(flow_decoder.disasm(bytes.fromhex(i['bytes']),i['rva'],count=1))
    if decoded.group(CS_GRP_JUMP):transfers[e['target']].append(dict(entry=u['entry'],source=e['source'],kind='import_tail_transfer',instruction_bytes=i['bytes'],import_symbol=json.loads(e['detail'])))
  contexts[u['module_sha256'],u['entry']]=dict(instruction_set_sha256=u['instruction_set_sha256'],after=after,transfers=transfers)
 def inspect(item):
  n,obj=item;folder=base/obj['source_batch']/obj['folder'];path=folder/'function.obj';assert sha(path)==obj['object_sha256'];cmd=[str(nm),'--format=posix','--no-demangle',str(path)]
  proc=subprocess.run(cmd,capture_output=True,timeout=120);(a.out/f'object-{n:04d}.nm.txt').write_bytes(proc.stdout);(a.out/f'object-{n:04d}.stderr').write_bytes(proc.stderr);assert proc.returncode==0,(path,proc.stderr)
  symbols=[]
  for line in proc.stdout.decode('utf-8').splitlines():
   m=re.fullmatch(r'(\S+) ([A-Za-z?]) ([0-9a-fA-F]+|-) ([0-9a-fA-F]+|-)',line);assert m,('unknown llvm-nm row',line)
   name,kind,address,size=m.groups();symbols.append(dict(name=name,kind=kind,address=address,size=size))
  actual={int(s['name'][4:],16) for s in symbols if s['kind']=='T' and re.fullmatch(r'sub_[0-9a-f]+',s['name'])}
  assert actual==set(obj['compiled_roots']),('actual function definitions differ from compiler audit',obj['folder'],actual^set(obj['compiled_roots']))
  audit=read(folder/'audit.json');assert set(audit['compiled_roots'])==actual
  units=read(folder/'units.json');assert {u['entry'] for u in units}==set(obj['entries'])
  missing=[];module_base=bases[obj['module']]
  for pc in audit['missing_instruction_starts']:
   rva=pc-module_base;predecessors=[];transfers=[]
   for u in units:
    context=contexts[obj['module'],u['entry']];assert u['instruction_set_sha256']==context['instruction_set_sha256']
    predecessors.extend(context['after'].get(rva,[]));transfers.extend(context['transfers'].get(rva,[]))
   missing.append(dict(logical_address=pc,module=obj['module'],rva=rva,target_is_compiled_root=pc in known_roots,preceding_control_contracts=predecessors,explicit_transfer_edges=transfers,dispatch_authorized=False))
  return dict(index=n,source_batch=obj['source_batch'],folder=obj['folder'],module=obj['module'],object_sha256=obj['object_sha256'],nm_sha256=sha(a.out/f'object-{n:04d}.nm.txt'),symbols=symbols,missing_blocks=missing)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(inspect,enumerate(active)):
   results.append(r)
   if len(results)%50==0:print(json.dumps(dict(objects_inspected=len(results))),flush=True)
 defined=collections.defaultdict(list);undefined=collections.defaultdict(list)
 for obj in results:
  for sym in obj['symbols']:
   if sym['kind']=='U':undefined[sym['name']].append(obj['index'])
   elif sym['kind'].isupper():defined[sym['name']].append(dict(object=obj['index'],kind=sym['kind']))
 duplicates={k:v for k,v in defined.items() if len(v)>1};missing_names=sorted(set(undefined)-set(defined));decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;images={};links={};relocs={};exports=collections.defaultdict(list)
 for h,name,path in modules:
  assert sha(path)==h;im=images[h]=ElfImage(Path(path).read_bytes());link=links[h]=im.linkage();relocs[h]={r['offset']:r for r in link['relocations']}
  for sym in link['symbols']:
   if sym['defined'] and sym['type']==2:exports[tuple(sym[k] for k in ('nid','library','module'))].append(dict(module=h,rva=sym['value'],logical_address=bases[h]+sym['value']))
 classifications=[]
 for name in missing_names:
  row=dict(symbol=name,objects=undefined[name]);match=re.fullmatch(r'sub_([0-9a-f]+)',name)
  if match:
   pc=int(match[1],16);mod=slot.get(pc&~0xffffffff);row.update(kind='unclassified logical target',logical_address=pc)
   if mod:
    h=mod['module'];rva=pc-mod['logical_base'];row.update(module=h,rva=rva);im=images[h]
    try:ins=next(decoder.disasm(im.at_va(rva,15),rva,count=1),None)
    except (ValueError,KeyError):ins=None
    if ins and ins.mnemonic=='jmp' and ins.operands[0].type==X86_OP_MEM and ins.operands[0].mem.base==X86_REG_RIP:
     rel=relocs[h].get(rva+ins.size+ins.operands[0].mem.disp)
     if rel and rel['type']==7:
      sym=links[h]['symbols'][rel['symbol']];candidates=exports.get(tuple(sym[k] for k in ('nid','library','module')),[])
      row.update(kind='import PLT requires native binding',stub_bytes=ins.bytes.hex(),relocation=rel,symbol_record=sym,bundled_candidates=[x|dict(compiled=x['logical_address'] in known_roots) for x in candidates],runtime_binding_validated=False)
  else:row['kind']='native support or host library symbol requires implementation/linkage'
  classifications.append(row)
 exits=[dict(object=obj['index'],**m) for obj in results for m in obj['missing_blocks']]
 for x in exits:
  imports_at_site=[e for e in x['explicit_transfer_edges'] if e['kind']=='import_tail_transfer']
  if imports_at_site:
   h=x['module'];rva=x['rva'];i=next(decoder.disasm(images[h].at_va(rva,15),rva,count=1));assert i.mnemonic=='jmp' and i.operands[0].type==X86_OP_MEM and i.operands[0].mem.base==X86_REG_RIP
   rel=relocs[h][rva+i.size+i.operands[0].mem.disp];assert rel['type']==7;sym=links[h]['symbols'][rel['symbol']]
   for edge in imports_at_site:assert all(edge['import_symbol'][k]==sym[k] for k in ('nid','library','module'))
   x['import_stub_evidence']=dict(bytes=i.bytes.hex(),relocation=rel,symbol=sym,runtime_binding_validated=False)
 alias_cases=[x for x in exits if x['target_is_compiled_root'] and x['preceding_control_contracts']]
 write_json(a.out/'objects.json',results);write_json(a.out/'unresolved-symbols.json',classifications);write_json(a.out/'duplicate-definitions.json',duplicates);write_json(a.out/'explicit-missing-blocks.json',exits);write_json(a.out/'known-target-after-contract.json',alias_cases)
 summary=dict(status='actual COFF linkage and explicit-exit inventory complete; native gate remains open',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),active_manifest=str(a.manifest),active_manifest_sha256=sha(a.manifest),llvm_nm_sha256=sha(nm),objects=len(results),compiled_roots=len(known_roots),defined_global_symbols=len(defined),undefined_symbol_names=len(undefined),unresolved_symbol_names=len(missing_names),unresolved_classes=dict(collections.Counter(x['kind'] for x in classifications)),duplicate_global_definitions=len(duplicates),explicit_missing_block_records=len(exits),missing_instruction_start_records=len(exits),emitted_ir_exit_sites_audited=False,missing_start_context_counts=dict(collections.Counter('after_control_contract' if x['preceding_control_contracts'] else 'compiled_target_transfer' if x['explicit_transfer_edges'] and x['target_is_compiled_root'] else 'import_tail_transfer' if x['explicit_transfer_edges'] and all(e['kind']=='import_tail_transfer' for e in x['explicit_transfer_edges']) else 'unclassified' for x in exits)),known_target_after_contract_records=len(alias_cases),unresolved_native_support_symbols=[x['symbol'] for x in classifications if x['kind'].startswith('native support')],unclassified_logical_targets=[x for x in classifications if x['kind']=='unclassified logical target'],artifact_sha256={name:sha(a.out/name) for name in ['objects.json','unresolved-symbols.json','duplicate-definitions.json','explicit-missing-blocks.json','known-target-after-contract.json']},
  limitations=['Read-only symbol/table inspection; no linking or game execution. A symbol definition is not a native control or ABI contract.','The missing-start list comes from compiler audit reads, not an exhaustive emitted-IR exit-site count. Optimized IR can merge starts, and separate dynamic unexpected-return exits need independent inspection.','Missing-block addresses can coincide with compiled entry points after nonreturn contracts. Never authorize dispatch from target availability alone; retain source/exit intent.','PLT relocation and supplied-export candidates remain conditional on native loader binding, mutation and code identity. Unknown logical targets and duplicate definitions require concrete investigation.'],p3_gate_passed=False,native_game_boot=False)
 write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
