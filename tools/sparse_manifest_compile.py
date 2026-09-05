"""Compile the twelve retained sparse callback/dependency manifests; never execute game code."""
import collections,json,re,sqlite3,subprocess,sys,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import environment,LLVM
from tools.formats import ElfImage
source,out,lifter=map(Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=False);lifter=lifter.resolve();env=environment();base=0x100000000
prior=Path('local/compiler-spike/callback-manifest-v1/results.json')
keys={(r['module_sha256'],r['entry']) for r in json.loads(prior.read_text()) if r['status']=='sparse_instruction_map_requires_lifter_adapter'}
assert len(keys)==12
units=[u for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8') if (u:=json.loads(line)) and (u['module_sha256'],u['entry']) in keys]
assert len(units)==12
units.sort(key=lambda u:(u['module_sha256'],u['entry']))
db=sqlite3.connect(f'{(source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True);images={}
for h,path in db.execute('SELECT hash,path FROM module'):
 if h in {k[0] for k in keys}:assert sha(path)==h;images[h]=ElfImage(Path(path).read_bytes())
write_json(out/'identity.json',dict(source_db_sha256=sha(source/'analysis.sqlite'),manifest_sha256=sha(source/'compilation-manifest.jsonl'),selection_sha256=sha(prior),lifter_sha256=sha(lifter),semantics_sha256=sha('build/remill/lib/Arch/X86/Runtime/amd64_avx.bc'),clang_sha256=sha(LLVM/'bin/clang.exe'),execution='none',object_flags=['-O2','-march=haswell','-mno-incremental-linker-compatible'],selection='All twelve sparse entries rejected by callback-manifest-v1, sorted by module/RVA.',root_policy='Entry, metadata landing pads, independently recovered table targets and in-map direct call targets; ordinary direct branches stay inside a trace.'))
results=[]
def run(cmd,folder,name):
 start=time.monotonic()
 with (folder/(name+'.stdout')).open('wb') as o,(folder/(name+'.stderr')).open('wb') as e:r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=120)
 return dict(argv=list(map(str,cmd)),exit_code=r.returncode,elapsed_seconds=time.monotonic()-start)
for u in units:
 h,entry=u['module_sha256'],u['entry'];folder=out/f'{h[:12]}-{entry:x}';folder.mkdir();write_json(folder/'manifest.json',u)
 assert not u['issues'];addresses={i['rva'] for i in u['instructions']};rows=[];seen=set()
 for i in u['instructions']:
  raw=bytes.fromhex(i['bytes']);assert len(raw)==i['size'] and images[h].at_va(i['rva'],i['size'])==raw
  extent=set(range(i['rva'],i['rva']+i['size']));assert not seen&extent;seen.update(extent)
  rows.append(dict(address=base+i['rva'],bytes=raw.hex()))
 roots={entry:'manifest entry'}
 for pad, in db.execute('SELECT DISTINCT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL',(h,entry)):
  assert pad in addresses;roots[pad]='LSDA landing-pad metadata'
 for edge in u['edges']:
  if edge['target_module']==h and edge['target'] in addresses and edge['kind'] in ('validated_jump_table','independently_recovered_jump_table','direct_call'):
   roots.setdefault(edge['target'],'explicit recovered target '+edge['kind'])
 data=dict(roots=[base+entry]+[base+r for r in sorted(roots) if r!=entry],instructions=rows)
 write_json(folder/'input.json',data);write_json(folder/'roots.json',[dict(rva=r,reason=reason) for r,reason in sorted(roots.items())])
 r=dict(module_sha256=h,entry=entry,folder=folder.name,instructions=len(rows),instruction_bytes=len(seen),analysis_span=max(seen)+1-min(seen),roots=len(roots),input_sha256=sha(folder/'input.json'),execution='not_executed')
 r['lift']=run([lifter,folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json'],folder,'lift')
 r['status']='lift_rejected'
 if r['lift']['exit_code']==0:
  audit=json.loads((folder/'audit.json').read_text());assert set(audit['decoded_addresses'])=={base+x for x in addresses};assert not audit['unvisited_manifest_instructions'];assert audit['input_bytes']==len(seen)
  boundaries=[]
  for pc in audit['missing_instruction_starts']:
   at=pc-base
   preceding=[i['rva'] for i in u['instructions'] if i['rva']+i['size']==at]
   reasons=[e for e in u['edges'] if (e['source'] in preceding and e['kind']=='annotated_control_contract_requires_runtime') or (e['target']==at and e['kind'] in ('direct_jump','cross_fence_jump'))]
   boundaries.append(dict(rva=at,evidence=reasons,classification='annotated control or external transfer' if reasons else 'unclassified missing path'))
  r['missing_boundaries']=boundaries;r['audit_sha256']=sha(folder/'audit.json')
  ir=(folder/'function.ll').read_text();r['external_declarations']=re.findall(r'^declare[^@]*@([^ (]+)',ir,re.M)
  r['unresolved_cpu_boundaries']=[s for s in r['external_declarations'] if s in ('__remill_missing_block','__remill_error','__remill_async_hyper_call','__remill_sync_hyper_call','__remill_jump','__remill_function_call') or s.startswith('sub_')]
  r['compile']=run([LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',folder/'function.obj'],folder,'compile')
  r['status']='object_built' if r['compile']['exit_code']==0 else 'object_failed'
  if r['status']=='object_built':r.update(object_sha256=sha(folder/'function.obj'),object_bytes=(folder/'function.obj').stat().st_size)
 write_json(folder/'result.json',r);results.append(r);print(json.dumps(dict(entry=hex(entry),status=r['status'],instructions=len(rows),roots=len(roots))),flush=True)
write_json(out/'results.json',results)
summary=dict(status='sparse manifest compilation complete; startup gate NOT passed',selected=len(results),results=dict(collections.Counter(r['status'] for r in results)),instructions=sum(r['instructions'] for r in results),input_bytes=sum(r['instruction_bytes'] for r in results),objects_bytes=sum(r.get('object_bytes',0) for r in results),roots=sum(r['roots'] for r in results),unclassified_missing_paths=sum(b['classification']=='unclassified missing path' for r in results for b in r.get('missing_boundaries',[])),objects_with_unresolved_cpu_boundaries=sum(bool(r.get('unresolved_cpu_boundaries')) for r in results),limitations='Only supplied instruction bytes are readable to the compiler; no filler or original game CPU execution. Compiling extra logical roots does not implement exception/indirect dispatch. Objects may define overlapping roots across units and were not linked. Runtime helpers, binding and control contracts remain open.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
raise SystemExit(any(r['status']!='object_built' for r in results))
