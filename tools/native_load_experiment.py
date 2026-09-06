"""Validate native private NX loading against independent Python relocated bytes."""
import argparse,copy,hashlib,json,struct,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
summary=read(a.plan/'summary.json');registry=summary['registry_identity_sha256']
for name,digest in summary['files'].items():assert sha(a.plan/name)==digest
regions=read(a.plan/'regions.json');bases={r['module']:r['logical_base'] for r in read(a.plan/'modules.json')};relocations=[];guards=[]
for row in map(json.loads,(a.plan/'relocations.jsonl').read_text().splitlines()):
 at=bases[row['module']]+row['offset']
 if row['value'] is None:guards.append(dict(base=at,size=8,identity=f"{row['module']}:{row['offset']:x}:{row['type']}"))
 else:relocations.append((at,row['value']))
assert len(relocations)+len(guards)==summary['relocations'] and len(guards)==37
rows=[dict(base=r['base'],size=r['mapped_size'],declared=r['declared_memory_size'],rights=r['native_rights'],initial=(a.plan/r['initial_file']).read_bytes()) for r in regions]
def bundle(rows,relocations,guards,identity):
 b=bytearray(b'BBLOAD01'+identity.encode('ascii')+struct.pack('<IIII',len(rows),len(relocations),len(guards),0))
 for r in rows:b+=struct.pack('<QQQQII',r['base'],r['size'],r['declared'],len(r['initial']),r['rights'],0)+r['initial']
 for at,value in relocations:b+=struct.pack('<QQ',at,value)
 for g in guards:
  name=g['identity'].encode('ascii');b+=struct.pack('<QQI',g['base'],g['size'],len(name))+name
 return b
def expected(rows,relocations,guards):
 buffers=[bytearray(r['initial'])+bytearray(r['size']-len(r['initial'])) for r in rows]
 for at,value in relocations:
  indexes=[n for n,r in enumerate(rows) if r['base']<=at and at+8<=r['base']+r['declared']];assert len(indexes)==1;n=indexes[0];struct.pack_into('<Q',buffers[n],at-rows[n]['base'],value)
 digest=hashlib.sha256();verified=0;skipped=0
 for n in sorted(range(len(rows)),key=lambda n:rows[n]['base']):
  r=rows[n];at=0
  for g in sorted(guards,key=lambda g:g['base']):
   if not r['base']<=g['base']<r['base']+r['size']:continue
   start=g['base']-r['base'];assert start>=at and start+g['size']<=r['size'];digest.update(buffers[n][at:start]);verified+=start-at;skipped+=g['size'];at=start+g['size']
  digest.update(buffers[n][at:]);verified+=r['size']-at
 return dict(status='private-load-validated',regions=len(rows),relocations=len(relocations),guards=len(guards),mapped_bytes=sum(r['size'] for r in rows),verified_bytes=verified,guarded_bytes=skipped,sha256_unguarded=digest.hexdigest(),game_execution=False)
def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
objects=[]
for name in ['fault','memory','loader','loader_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'loader.exe')])
# Authored data only; the one-byte RET is never executable or called.
authored=[dict(base=0x100000000,size=4096,declared=4096,rights=3,initial=bytes(range(16))),dict(base=0x200000000,size=4096,declared=4096,rights=5,initial=bytes([0xc3]))];rels=[(0x100000010,0x123456789abcdef)];blocks=[dict(base=0x100000018,size=8,identity='authored-unresolved')];auth_id='1'*64;auth=bundle(authored,rels,blocks,auth_id);path=out/'authored.bin';path.write_bytes(auth);run('authored',[out/'loader.exe',path,sha(path),auth_id,'validate']);assert read(out/'authored.stdout')==expected(authored,rels,blocks)
negative=[]
for mode,message in [('overlap','overlapping load regions'),('code-reloc','relocation is not writable data'),('outside','relocation/guard outside declared memory'),('duplicate-reloc','overlapping relocation destinations'),('resolved-guard','guard overlaps resolved relocation'),('duplicate-guard','overlapping loader guards'),('native-slot','native service slot collision'),('truncated','truncated load bundle'),('trailing','trailing load bundle bytes'),('hash','load bundle SHA256 mismatch'),('registry','load bundle registry identity')]:
 rr=copy.deepcopy(authored);rl=rels.copy();gg=copy.deepcopy(blocks);identity=auth_id
 if mode=='overlap':rr[1]['base']=rr[0]['base']
 if mode=='code-reloc':rl=[(rr[1]['base'],1)]
 if mode=='outside':rr[0]['declared']=16
 if mode=='duplicate-reloc':rl+=rl
 if mode=='resolved-guard':gg[0]['base']=rl[0][0]
 if mode=='duplicate-guard':gg+=gg
 if mode=='native-slot':rr[1]['base']=0x900000000
 raw=bundle(rr,rl,gg,auth_id)
 if mode=='truncated':raw=raw[:-5]
 if mode=='trailing':raw+=b'x'
 if mode=='hash':raw[-1]^=1
 if mode=='registry':identity='2'*64
 path=out/(mode+'.bin');path.write_bytes(raw);run(mode,[out/'loader.exe',path,hashlib.sha256(auth).hexdigest() if mode=='hash' else sha(path),identity,'validate'],2);assert message in (out/(mode+'.stderr')).read_text();negative.append(dict(mode=mode,required_diagnostic=message))
reference=expected(rows,relocations,guards);write_json(out/'expected.json',reference);path=out/'modules.bin';path.write_bytes(bundle(rows,relocations,guards,registry));bundle_sha=sha(path);run('game-data',[out/'loader.exe',path,bundle_sha,registry,'validate']);actual=read(out/'game-data.stdout');assert actual==reference
ordered=sorted(guards,key=lambda g:g['base'])
for n,guard in enumerate(ordered):
 label=f'guard-{n:02d}';run(label,[out/'loader.exe',path,bundle_sha,registry,'guard',n],0xb0000008);fault,detail=[json.loads(s) for s in (out/(label+'.stderr')).read_text().splitlines()];assert fault['boundary']=='unresolved-relocation' and int(fault['address'],16)==guard['base'] and fault['width']==1;assert detail['unresolved_identity']==guard['identity'] and detail['completed_memory_operations']==0
write_json(out/'guards.json',ordered);result=dict(status='private native loading and independent relocated-byte checks pass',plan_sha256=sha(a.plan/'summary.json'),registry_identity=registry,bundle_sha256=bundle_sha,actual=actual,authored=read(out/'authored.stdout'),setup_rejections=negative,unresolved_guard_probes=len(guards),native_objects={p.name:sha(p) for p in objects},source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native/runtime').glob('*') if p.is_file()},game_execution=False,limitations=['All source/game views unchanged; bundle is a fresh copy.','Runtime applies only explicitly resolved planned values. All 37 unresolved slots remain guarded against reads and writes.','Independent digest covers every unguarded byte including BSS, alignment tail and relocations; guarded bytes are excluded, not assigned meaning.','No game entry, initializer, callback, TLS allocation, target FP profile or native service is executed.','Static module/version/interposition assumptions remain conditional.'])
write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],actual=actual,setup_rejections=len(negative),guard_probes=len(guards))),flush=True)
