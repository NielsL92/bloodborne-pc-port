"""Stable native data bundle encoding and independent relocated-byte digest."""
import hashlib,struct
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
