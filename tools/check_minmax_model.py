"""Check integer min/max modeling against recorded authored hardware observations."""
import json,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);checked=0;old_mismatches=0
for row in map(json.loads,(source/'execute.stdout').open()):
 if row['operation']>1:continue
 flags=0;old_flags=0;result=[]
 for a,b in zip(row['input'][:4],row['input'][4:]):
  nan=(a&0x7fffffff)>0x7f800000 or (b&0x7fffffff)>0x7f800000
  da=0<(a&0x7fffffff)<0x800000;db=0<(b&0x7fffffff)<0x800000
  if row['control']&64:
   if da:a&=0x80000000
   if db:b&=0x80000000
  elif da or db:
   old_flags|=2
   if not nan:flags|=2
  if nan:flags|=1;old_flags|=1;result.append(b);continue
  ka=(~a&0xffffffff) if a&0x80000000 else a|0x80000000;kb=(~b&0xffffffff) if b&0x80000000 else b|0x80000000
  result.append(b if ((a|b)&0x7fffffff)==0 else (a if (ka<kb if row['operation']==0 else ka>kb) else b))
 csr=row['control']|flags;fault=bool(flags&~(row['control']>>7)&63)
 old_mismatches+=((row['control']|old_flags)!=row['csr'])
 assert csr==row['csr'] and fault==bool(row['code']) and (fault or result==row['output']),row
 checked+=1
assert checked==8192 and old_mismatches==384
summary=dict(status='integer min/max result and floating-state model matches characterization',checked=checked,naive_denormal_flag_mismatches=old_mismatches,raw_sha256=sha(source/'execute.stdout'),finding='A NaN suppresses a denormal flag from the same pair; other vector lanes may still raise denormal. DAZ preprocessing preserves the zero sign. Raised bits update MXCSR before an unmasked fault; destination is unchanged on fault. Native Windows exception code is not used as the guest exception identity.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
