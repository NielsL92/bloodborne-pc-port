"""Recompile selected complete objects using their exact verified sparse inputs."""
import argparse,concurrent.futures,json,re,subprocess,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM,environment
p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base=Path('local/compiler-spike').resolve();env=environment()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
rows=read(a.plan);mappings=[read(base/r['source_batch']/'identity.json')['module_mapping'] for r in rows];assert all(m==mappings[0] for m in mappings)
write_json(a.out/'identity.json',dict(plan_sha256=sha(a.plan),lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),semantics_directory=str(a.semantics.resolve()),clang_sha256=sha(LLVM/'bin/clang.exe'),module_mapping=mappings[0],object_flags=['-O2','-march=haswell','-mno-incremental-linker-compatible'],execution='none; exact static inputs only'))
def compile_one(row):
 old=base/row['source_batch']/row['folder'];folder=a.out/f"batch-{row['index']:04d}";folder.mkdir();assert sha(old/'function.obj')==row['object_sha256']
 for name,key in [('input.json','input_sha256'),('roots.json','roots_sha256'),('units.json','units_sha256')]:
  assert sha(old/name)==row[key];(folder/name).write_bytes((old/name).read_bytes())
 steps=[]
 def run(name,argv):
  start=time.monotonic()
  with (folder/(name+'.stdout')).open('wb') as stdout,(folder/(name+'.stderr')).open('wb') as stderr:proc=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
  steps.append(dict(name=name,argv=list(map(str,argv)),exit_code=proc.returncode,elapsed_seconds=time.monotonic()-start));write_json(folder/'steps.json',steps);assert proc.returncode==0,(row['index'],name)
 run('lift',[a.lifter.resolve(),(folder/'input.json').resolve(),(folder/'function.bc').resolve(),(folder/'function.ll').resolve(),(folder/'audit.json').resolve(),a.semantics.resolve()])
 audit=read(folder/'audit.json');data=read(folder/'input.json');assert audit['compiled_roots']==row['compiled_roots']==data['roots'];assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions']
 bases={m['module']:m['logical_base'] for m in mappings[0]};selectors={s['address']:s for s in audit['decoded_selectors']}
 for site in row.get('sites',[]):
  binding=selectors[bases[site['module']]+site['rva']];expected=site.get('expected_implementation',('BB_COMISS' if site['mnemonic'].endswith('ss') else 'BB_COMISD'));assert binding['lifted'] and expected in binding['implementation']
 run('compile',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',folder/'function.obj'])
 result=dict(folder=folder.name,module=row['module'],entries=row['entries'],compiled_roots=audit['compiled_roots'],object_sha256=sha(folder/'function.obj'),object_bytes=(folder/'function.obj').stat().st_size,input_sha256=sha(folder/'input.json'),audit_sha256=sha(folder/'audit.json'),instructions=len(data['instructions']),roots=len(data['roots']),missing_instruction_starts=audit['missing_instruction_starts'],external_declarations=re.findall(r'^declare[^@]*@([^ (]+)',(folder/'function.ll').read_text(encoding='utf-8'),re.M),status='object_built',execution='not_executed',replaces=dict(source_batch=row['source_batch'],folder=row['folder'],object_sha256=row['object_sha256']),original_missing_instruction_starts=read(old/'audit.json')['missing_instruction_starts'])
 assert result['missing_instruction_starts']==result['original_missing_instruction_starts'];write_json(folder/'result.json',result);print(json.dumps(dict(object=row['index'],status='compiled',entries=len(row['entries']))),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(compile_one,rows))
write_json(a.out/'results.json',results);summary=dict(status='selected complete objects recompiled; native gate remains open',objects=len(results),entries=sum(len(r['entries']) for r in results),compiled_roots=sum(r['roots'] for r in results),instructions=sum(r['instructions'] for r in results),object_bytes=sum(r['object_bytes'] for r in results),missing_start_records=sum(len(r['missing_instruction_starts']) for r in results),all_missing_start_lists_unchanged=True,game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
