"""Compile complete prepared objects with source-aware exits; never link or execute."""
import argparse,concurrent.futures,json,re,subprocess,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM,environment
p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--indices');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);env=environment()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
rows=read(a.plan/'objects.json')
if a.indices:
 selected={int(n) for n in a.indices.split(',')};rows=[r for r in rows if r['index'] in selected];assert len(rows)==len(selected)
identity=read(a.plan/'identity.json');identity.update(plan_sha256=sha(a.plan/'objects.json'),lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),semantics_directory=str(a.semantics.resolve()),clang_sha256=sha(LLVM/'bin/clang.exe'),object_flags=['-O2','-march=haswell','-mno-incremental-linker-compatible']);write_json(a.out/'identity.json',identity)
def compile_one(row):
 folder=a.out/f"batch-{row['index']:04d}";folder.mkdir();steps=[]
 try:
  prepared=a.plan/row['prepared_folder'];old=Path('local/compiler-spike')/row['source_batch']/row['folder'];assert sha(old/'function.obj')==row['object_sha256']
  for name,key in [('input.json','input_sha256'),('roots.json','roots_sha256'),('units.json','units_sha256')]:assert sha(prepared/name)==row[key];(folder/name).write_bytes((prepared/name).read_bytes())
  def run(name,argv):
   start=time.monotonic()
   with (folder/(name+'.stdout')).open('wb') as stdout,(folder/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=240)
   steps.append(dict(name=name,argv=list(map(str,argv)),exit_code=r.returncode,elapsed_seconds=time.monotonic()-start));write_json(folder/'steps.json',steps);assert r.returncode==0,name
  run('lift',[a.lifter.resolve(),(folder/'input.json').resolve(),(folder/'function.bc').resolve(),(folder/'function.ll').resolve(),(folder/'audit.json').resolve(),a.semantics.resolve()])
  data=read(folder/'input.json');audit=read(folder/'audit.json');assert audit['compiled_roots']==row['compiled_roots']==data['roots'];assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions'];assert audit['missing_instruction_starts']==row['original_missing_instruction_starts']
  assert audit.get('native_memory_provenance',False)==data.get('native_memory_provenance',False)
  expected={r['address']:r for r in data['return_contracts']};guarded={r['source'] for r in audit['call_return_checks'] if r['no_normal_return']};assert guarded==set(expected)
  for r in audit['call_return_checks']:
   if r['no_normal_return']:assert r['provenance']==expected[r['source']]['provenance'] and r['expected_next_pc']==expected[r['source']]['expected_next_pc'] and r['kind']=='ordinary-call'
  run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',folder/'function.obj'])
  result=dict(index=row['index'],folder=folder.name,module=row['module'],entries=row['entries'],compiled_roots=audit['compiled_roots'],object_sha256=sha(folder/'function.obj'),object_bytes=(folder/'function.obj').stat().st_size,input_sha256=sha(folder/'input.json'),audit_sha256=sha(folder/'audit.json'),instructions=len(data['instructions']),roots=len(data['roots']),missing_instruction_starts=audit['missing_instruction_starts'],call_return_checks=len(audit['call_return_checks']),nonreturn_checks=sum(r['no_normal_return'] for r in audit['call_return_checks']),hypercall_checks=sum(r['kind']=='asynchronous-hypercall' for r in audit['call_return_checks']),missing_block_exits=len(audit['missing_block_exits']),external_declarations=re.findall(r'^declare[^@]*@([^ (]+)',(folder/'function.ll').read_text(encoding='utf-8'),re.M),status='object_built',execution='not_executed',replaces=dict(source_batch=row['source_batch'],folder=row['folder'],object_sha256=row['object_sha256']))
 except Exception as e:result=dict(index=row['index'],folder=folder.name,status='failed',error=str(e),execution='not_executed')
 write_json(folder/'result.json',result);print(json.dumps(dict(index=row['index'],status=result['status'])),flush=True);return result
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(compile_one,rows):results.append(result)
write_json(a.out/'results.json',results);good=[r for r in results if r['status']=='object_built'];summary=dict(status='all selected objects compiled with sourced exits' if len(good)==len(rows) else 'compiler gate failed; all results retained',objects=len(good),failed=len(rows)-len(good),entries=sum(len(r['entries']) for r in good),compiled_roots=sum(r['roots'] for r in good),instructions=sum(r['instructions'] for r in good),object_bytes=sum(r['object_bytes'] for r in good),missing_start_records=sum(len(r['missing_instruction_starts']) for r in good),call_return_checks=sum(r['call_return_checks'] for r in good),nonreturn_checks=sum(r['nonreturn_checks'] for r in good),hypercall_checks=sum(r['hypercall_checks'] for r in good),missing_block_exits=sum(r['missing_block_exits'] for r in good),game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True);raise SystemExit(0 if len(good)==len(rows) else 1)
