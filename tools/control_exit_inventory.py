"""Run the LLVM API inspector over actual saved bitcode, without execution."""
import argparse,collections,concurrent.futures,json,re,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('inspector',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike');active=json.loads(a.manifest.read_text(encoding='utf-8'))
 def inspect(item):
  n,obj=item;folder=base/obj['source_batch']/obj['folder'];assert sha(folder/'function.obj')==obj['object_sha256'];output=a.out/f'object-{n:04d}.json';command=[str(a.inspector.resolve()),str((folder/'function.bc').resolve()),str(output.resolve())]
  proc=subprocess.run(command,capture_output=True,timeout=180);(a.out/f'object-{n:04d}.stdout').write_bytes(proc.stdout);(a.out/f'object-{n:04d}.stderr').write_bytes(proc.stderr);assert proc.returncode==0,(n,proc.stderr)
  report=json.loads(output.read_text(encoding='utf-8'));actual={int(f['name'][4:],16) for f in report['functions']};assert actual==set(obj['compiled_roots'])
  return dict(index=n,source_batch=obj['source_batch'],folder=obj['folder'],object_sha256=obj['object_sha256'],bitcode_sha256=sha(folder/'function.bc'),report_sha256=sha(output),report=report)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for row in pool.map(inspect,enumerate(active)):
   results.append(row)
   if len(results)%50==0:print(json.dumps(dict(bitcode_objects_inspected=len(results))),flush=True)
 counts=collections.Counter();site_attrs=collections.Counter();definition_attrs=collections.Counter();pc_kinds=collections.Counter();decls=collections.defaultdict(list);missing=[];errors=[];error_origins=collections.Counter()
 for obj in results:
  r=obj['report'];counts.update(r['site_counts'])
  for f in r['functions']:definition_attrs[(f['calling_convention'],f['nounwind'],f['noreturn'])]+=1
  for d in r['declarations']:decls[d['name']].append(dict(object=obj['index'],**d))
  for s in r['sites']:
   site_attrs[(s['callee'],s['nounwind'],s['noreturn'],s['is_invoke'])]+=1
   if s['callee']=='__remill_error':
    names=s['successor_names'];matches=[re.match(r'^_ZN12_GLOBAL__N_1[0-9]+(IDIVrdxrax|IDIVedxeax|DIVrdxrax|DIVedxeax|COMISS|COMISD)I',name) for name in names]
    origin=matches[0].group(1) if len(matches)==1 and matches[0] else 'unclassified'
    error_origins[origin]+=1;errors.append(dict(object=obj['index'],semantic_origin_from_retained_block_name=origin,**s))
   if s['callee']=='__remill_missing_block':
    assert len(s['arguments'])==3;pc_kinds[s['arguments'][1]['kind']]+=1;missing.append(dict(object=obj['index'],**s))
 compact=[{k:v for k,v in obj.items() if k!='report'} for obj in results];write_json(a.out/'objects.json',compact);write_json(a.out/'declarations.json',dict(decls));write_json(a.out/'missing-block-sites.json',missing);write_json(a.out/'error-sites.json',errors)
 summary=dict(status='all saved bitcode control sites inventoried; native boundary handling remains unvalidated',active_manifest=str(a.manifest),active_manifest_sha256=sha(a.manifest),inspector_sha256=sha(a.inspector),objects=len(results),compiled_functions=sum(len(x['report']['functions']) for x in results),site_counts=dict(counts),function_attribute_counts=[dict(calling_convention=k[0],nounwind=k[1],noreturn=k[2],count=v) for k,v in sorted(definition_attrs.items())],control_site_attribute_counts=[dict(callee=k[0],nounwind=k[1],noreturn=k[2],is_invoke=k[3],count=v) for k,v in sorted(site_attrs.items())],missing_block_pc_value_kinds=dict(pc_kinds),error_semantic_origin_counts=dict(error_origins),error_attribution='Retained optimized successor block names identify the inlined semantic family, not the precise guest instruction or a verified fault contract.',indirect_llvm_calls=sum(x['report']['indirect_llvm_calls'] for x in results),artifact_sha256={name:sha(a.out/name) for name in ['objects.json','declarations.json','missing-block-sites.json','error-sites.json']},limitations=['Actual LLVM API parse and verification of retained bitcode, with root identities compared to current COFF-backed manifests; no JIT, linking or game execution.','These are optimized IR call sites, not execution counts or one-to-one machine instruction/CFG-edge counts. Different starts can merge and dynamic return guards can add exits.','The same __remill_error hook is used by semantic StopFailure paths and compiler error paths; retained block names classify this census, not hardware behavior.','nounwind is a compiler contract. Native handlers must honor it or the compiler/call-site contract must be changed and independently validated; availability of C++ exceptions does not authorize throwing across it.'],p3_gate_passed=False,native_game_boot=False)
 write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
