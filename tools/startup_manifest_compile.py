"""Build bounded entry objects from exact recovered manifests; never execute them."""
import argparse,collections,json,re,sqlite3,subprocess,sys,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import environment,LLVM
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('--limit',type=int,default=128);p.add_argument('--entries',type=Path);a=p.parse_args()
if a.limit<1:p.error('--limit must be positive')
a.out.mkdir(parents=True,exist_ok=False)
units=[json.loads(line) for line in (a.source/'compilation-manifest.jsonl').open(encoding='utf-8')]
constructors=sorted((r for r in units if r['constructor_ordinal'] is not None),key=lambda r:r['constructor_ordinal'])
selected=[constructors[i*(len(constructors)-1)//(a.limit-1)] for i in range(a.limit)] if a.limit>1 else constructors[:1]
selection=f'{a.limit} evenly spaced invocation ordinals including first and last; size/gaps are not filtered out'
if a.entries:
 requested=json.loads(a.entries.read_text());keys={(r['module'],r['start']) for r in requested}
 selected=sorted((r for r in units if (r['module_sha256'],r['entry']) in keys),key=lambda r:(r['module_sha256'],r['entry']))
 assert len(selected)==len(keys),'requested entry absent from manifest'
 selected=selected[:a.limit];selection='Explicit entry list in module/RVA order; size/gaps are not filtered out'
lifter=Path('build/remill/bin/lift/remill-lift-21.exe').resolve();clang=LLVM/'bin/clang.exe';env=environment()
db=sqlite3.connect(f'{(a.source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True);images={}
for h,path in db.execute('SELECT hash,path FROM module'):
 if h not in {r['module_sha256'] for r in selected}:continue
 assert sha(path)==h;images[h]=ElfImage(Path(path).read_bytes())
write_json(a.out/'identity.json',dict(manifest_sha256=sha(a.source/'compilation-manifest.jsonl'),modules=sorted(images),lifter_sha256=sha(lifter),clang_sha256=sha(clang),flags=['amd64_avx','windows','O2','march=haswell'],selection=selection,entries_sha256=sha(a.entries) if a.entries else None,execution='none'))
results=[]
def run(command,folder,step):
 start=time.monotonic()
 with (folder/(step+'.stdout')).open('wb') as stdout,(folder/(step+'.stderr')).open('wb') as stderr:
  result=subprocess.run(list(map(str,command)),env=env,stdout=stdout,stderr=stderr,timeout=120)
 return dict(argv=list(map(str,command)),exit_code=result.returncode,seconds=time.monotonic()-start)
for n,u in enumerate(selected):
 folder=a.out/(f"{u['module_sha256'][:12]}-{u['entry']:x}" if a.entries else f"{u['entry']:x}");folder.mkdir();write_json(folder/'manifest.json',u)
 r=dict(module_sha256=u['module_sha256'],entry=u['entry'],folder=folder.name,ordinal=u['constructor_ordinal'],instructions=len(u['instructions']),execution='not_executed')
 im=images[u['module_sha256']]
 addresses={i['rva']+offset for i in u['instructions'] for offset in range(i['size'])}
 if u['issues'] or not addresses or min(addresses)!=u['entry']:
  r['status']='quarantined_manifest'
 elif len(addresses)!=max(addresses)+1-u['entry']:
  r['status']='sparse_instruction_map_requires_lifter_adapter'
 else:
  body=im.at_va(u['entry'],len(addresses));expected=b''.join(bytes.fromhex(i['bytes']) for i in u['instructions'])
  assert body==expected
  (folder/'bytes.bin').write_bytes(body);r['input_sha256']=sha(folder/'bytes.bin')
  r['lift']=run([lifter,'--arch=amd64_avx','--os=windows',f"--address={0x100000000+u['entry']}",f'--bytes_file={folder}/bytes.bin',f'--bc_out={folder}/function.bc',f'--ir_out={folder}/function.ll'],folder,'lift')
  r['status']='lift_failed'
  if r['lift']['exit_code']==0:
   ir=(folder/'function.ll').read_text();r['external_declarations']=re.findall(r'^declare[^@]*@([^ (]+)',ir,re.M)
   r['unresolved_cpu_boundaries']=[s for s in r['external_declarations'] if s in ('__remill_missing_block','__remill_error','__remill_async_hyper_call','__remill_sync_hyper_call','__remill_jump','__remill_function_call') or s.startswith('sub_')]
   r['compile']=run([clang,'-c','-O2','-march=haswell',folder/'function.bc','-o',folder/'function.obj'],folder,'compile')
   r['status']='object_built' if r['compile']['exit_code']==0 else 'object_failed'
   if r['status']=='object_built':r.update(object_sha256=sha(folder/'function.obj'),object_bytes=(folder/'function.obj').stat().st_size)
 write_json(folder/'result.json',r);results.append(r)
 if (n+1)%16==0:print(json.dumps(dict(attempted=n+1,statuses=dict(collections.Counter(r['status'] for r in results)))),flush=True)
write_json(a.out/'results.json',results)
summary=dict(status='bounded manifest compilation survey; startup execution gate NOT passed',selected=len(results),results=dict(collections.Counter(r['status'] for r in results)),objects_with_unresolved_cpu_boundaries=sum(bool(r.get('unresolved_cpu_boundaries')) for r in results),object_bytes=sum(r.get('object_bytes',0) for r in results),limitations='Objects retain external Remill memory/control helpers. No runtime link, execution, exception safety, dispatch closure, or speed claim. Sparse inputs are rejected, never flattened with data or filler.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
