"""Generate static native tables from exact compiled inputs and verified PLT evidence."""
import argparse,collections,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_MEM
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('active',type=Path);p.add_argument('dispatch',type=Path);p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('--ghidra-segments',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
active=read(a.active);dispatch=read(a.dispatch/'summary.json');assert dispatch['active_manifest_sha256']==sha(a.active);imports=read(a.dispatch/'native-import-stubs.json');pairs=read(a.dispatch/'source-target-pairs.json');assert sha(a.dispatch/'source-target-pairs.json')==dispatch['pairs_sha256'];assert sha(a.dispatch/'native-import-stubs.json')==dispatch['runtime_import_registry_sha256']
roots={};objects=[];x87={};input_instructions={};decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;mapping=None
for index,obj in enumerate(active):
 folder=ROOT/'local/compiler-spike'/obj['source_batch']/obj['folder'];identity=read(folder.parent/'identity.json')
 if mapping is None:mapping=identity['module_mapping']
 assert mapping==identity['module_mapping'];assert sha(folder/'function.obj')==obj['object_sha256'];audit=read(folder/'audit.json');assert set(audit['compiled_roots'])==set(obj['compiled_roots'])
 for pc in obj['compiled_roots']:assert pc not in roots;roots[pc]=dict(pc=pc,module=obj['module'],object=index)
 objects.append(dict(index=index,path=str(folder/'function.obj'),sha256=obj['object_sha256'],input_sha256=sha(folder/'input.json'),audit_sha256=sha(folder/'audit.json'),bitcode_sha256=sha(folder/'function.bc')))
 if audit['x87_opcode_immediates']:
  instructions={r['address']:r['bytes'] for r in read(folder/'input.json')['instructions']}
  for row in audit['x87_opcode_immediates']:
   pc=row['address'];code=instructions[pc];raw=bytes.fromhex(code);ins=next(decoder.disasm(raw,pc,count=1));assert ins.size==len(raw)
   i=next(i for i,v in enumerate(raw) if 0xd8<=v<=0xdf);fop=((raw[i]&7)<<8)|raw[i+1];assert fop==row['corrected'];memory=[o.mem for o in ins.operands if o.type==X86_OP_MEM];assert len(memory)<=1
   segment='None';uncertainty=None;base=None
   if memory:
    mem=memory[0];base=ins.reg_name(mem.base);explicit=ins.reg_name(mem.segment)
    if explicit:segment=explicit.upper();assert segment in ['ES','CS','SS','DS','FS','GS']
    elif base in ['rbp','rsp','ebp','esp']:segment='SS'
    elif base in ['r12','r13','r12d','r13d']:segment=None;uncertainty='default segment for extended stack/base register requires independent check'
    else:segment='DS'
   record=dict(pc=pc,module=obj['module'],bytes=code,instruction=ins.mnemonic+' '+ins.op_str,fop=fop,data_segment=segment,memory_base=base,uncertainty=uncertainty)
   if pc in x87:assert x87[pc]==record
   x87[pc]=record
# Re-check candidate export identity against supplied module symbol tables.
db=sqlite3.connect(a.source.resolve().joinpath('analysis.sqlite').as_uri()+'?mode=ro',uri=True);modules={h:dict(name=n,path=p) for h,n,p in db.execute('SELECT hash,name,path FROM module')};db.close();bases={r['module']:r['logical_base'] for r in mapping};exports=collections.defaultdict(list);module_records=[]
for h,info in modules.items():
 path=Path(info['path']);assert sha(path)==h;image=ElfImage(path.read_bytes());linkage=image.linkage();module_records.append(dict(module=h,name=info['name'],path=str(path),logical_base=bases[h]))
 for symbol in linkage['symbols']:
  if symbol['defined'] and symbol['type']==2:exports[tuple(symbol[k] for k in ['nid','library','module'])].append(dict(module=h,rva=symbol['value'],pc=bases[h]+symbol['value'],symbol_index=symbol['index']))
import_rows=[]
for row in imports:
 symbol=row['symbol_record'];pc=row['logical_address'];assert pc==bases[row['module']]+row['rva'] and pc not in roots and row['relocation']['type']==7
 candidates=exports.get(tuple(symbol[k] for k in ['nid','library','module']),[]);eligible=[c for c in candidates if c['pc'] in roots]
 for known in row.get('bundled_candidates',[]):assert any(c['module']==known['module'] and c['rva']==known['rva'] and c['pc']==known['logical_address'] for c in candidates)
 selected=eligible[0] if len(candidates)==len(eligible)==1 else None
 import_rows.append(dict(pc=pc,source_module=row['module'],rva=row['rva'],nid=symbol['nid'],library=symbol['library'],module=symbol['module'],stub_bytes=row['stub_bytes'],relocation=row['relocation'],candidates=candidates,compiled_export=selected['pc'] if selected else 0,binding='conditional static compiled export' if selected else 'explicit unimplemented native service',runtime_execution_validated=False))
import_rows.sort(key=lambda r:r['pc']);assert len({r['pc'] for r in import_rows})==len(import_rows);import_pcs={r['pc'] for r in import_rows}
pair_keys=[(r['source'],r['requested_target']) for r in pairs];assert pair_keys==sorted(set(pair_keys));assert all(target in roots or target in import_pcs for source,target in pair_keys)
segment_evidence=dict(status='unresolved segment metadata remains explicit',ghidra_boundary_checks=[])
if a.ghidra_segments:
 observed={}
 for module in read(a.ghidra_segments/'summary.json')['modules']:
  for window in read(a.ghidra_segments/module['name']/'ghidra.json'):
   for ins in window['instructions']:observed[module['module'],bases[module['module']]+ins['rva']]=ins
 for pc,row in x87.items():
  if row['uncertainty']:
   ins=observed[row['module'],pc];assert ins['bytes']==row['bytes'] and ins['length']*2==len(row['bytes']);assert row['memory_base'].upper() in ins['text'];segment_evidence['ghidra_boundary_checks'].append(dict(pc=pc,bytes=row['bytes'],ghidra_text=ins['text'],segment_selection_validated=False))
 segment_evidence['ghidra_summary_sha256']=sha(a.ghidra_segments/'summary.json')
write_json(a.out/'segment-evidence.json',segment_evidence)
write_json(a.out/'objects.json',objects);write_json(a.out/'targets.json',[roots[pc] for pc in sorted(roots)]);write_json(a.out/'imports.json',import_rows);write_json(a.out/'source-target-pairs.json',pairs);write_json(a.out/'x87-sites.json',[x87[pc] for pc in sorted(x87)]);write_json(a.out/'modules.json',sorted(module_records,key=lambda r:r['logical_base']))
identity=dict(active_manifest_sha256=sha(a.active),dispatch_summary_sha256=sha(a.dispatch/'summary.json'),files={name:sha(a.out/name) for name in ['objects.json','targets.json','imports.json','source-target-pairs.json','x87-sites.json','modules.json','segment-evidence.json']},conditional_binding='Unique exact NID/library/module and compiled export only; loader identity/relocations, initialization and interposition remain runtime obligations.',guest_execution=False,fp_profile_selected=False)
write_json(a.out/'identity.json',identity);digest=sha(a.out/'identity.json');q=json.dumps
lines=['// Generated static native registry. No game entry is called by the validator.','#include "runtime.h"','#include "registry.h"']
lines += [f'extern "C" Memory* sub_{pc:x}(State*,uint64_t,Memory*);' for pc in sorted(roots)]
lines += [f'extern "C" Memory* sub_{r["pc"]:x}(State* s,uint64_t pc,Memory* m) noexcept '+'{return bb_runtime::imported(s,pc,m);}' for r in import_rows]
lines += ['namespace bb_registry {','static const bb_runtime::Target targets[]={']+[f'{{{pc}ULL,sub_{pc:x}}},' for pc in sorted(roots)]+['};','static const bb_runtime::Import imports[]={']
lines += ['{'+','.join([str(r['pc'])+'ULL',q(r['nid']),q(r['library']),q(r['module']),'nullptr',str(r['compiled_export'])+'ULL'])+'},' for r in import_rows]+['};','static const bb_runtime::SourcePair pairs[]={']
lines += [f'{{{source}ULL,{target}ULL}},' for source,target in pair_keys]+['};',f'const bb_runtime::Tables tables{{targets,{len(roots)},pairs,{len(pairs)},imports,{len(import_rows)},{q(digest)}}};','const bb_runtime::Target import_gateways[]={']
lines += [f'{{{r["pc"]}ULL,sub_{r["pc"]:x}}},' for r in import_rows]+['};',f'const size_t import_gateway_count={len(import_rows)};','const bb_runtime::X87Site x87_sites[]={']
lines += [f'{{{pc}ULL,{r["fop"]},bb_runtime::Segment::{r["data_segment"]}}},' for pc,r in sorted(x87.items()) if r['data_segment'] is not None]+['};',f'const size_t x87_site_count={sum(r["data_segment"] is not None for r in x87.values())};','}']
(a.out/'registry.cpp').write_text(chr(10).join(lines)+chr(10),encoding='utf-8')
summary=dict(status='native registry generated without execution',objects=len(objects),roots=len(roots),source_pairs=len(pairs),imports=len(import_rows),compiled_export_bindings=sum(bool(r['compiled_export']) for r in import_rows),explicit_native_stops=sum(not r['compiled_export'] for r in import_rows),x87_sites=len(x87),x87_segments=dict(collections.Counter(r['data_segment'] if r['data_segment'] is not None else '<unresolved>' for r in x87.values())),unresolved_x87_sites=[r for r in x87.values() if r['uncertainty']],identity_sha256=digest,registry_sha256=sha(a.out/'registry.cpp'),game_execution=False,fp_profile_selected=False)
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
