"""Validate a binary32 square-root model against the authored state probe."""
import json,math,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);checked=0
for row in map(json.loads,(source/'execute.stdout').open()):
 if row['operation']!=2:continue
 raised=0;precision=False;result=[];control=row['control']
 for bits in row['input'][4:]:
  magnitude=bits&0x7fffffff;sign=bits&0x80000000
  if magnitude>0x7f800000:
   if not bits&0x400000:raised|=1
   result.append(bits|0x400000);continue
  if control&64 and magnitude<0x800000:result.append(sign);continue
  if not magnitude:result.append(bits);continue
  if sign:raised|=1;result.append(0xffc00000);continue
  if magnitude==0x7f800000:result.append(bits);continue
  mantissa=bits&0x7fffff;exponent=(bits>>23)-127
  if bits&0x7f800000:mantissa|=0x800000
  else:
   raised|=2;exponent=-126
   while mantissa<0x800000:mantissa*=2;exponent-=1
  odd=exponent%2;n=mantissa<<(23+odd);q=math.isqrt(n);remainder=n-q*q;precision|=bool(remainder);mode=(control>>13)&3
  if (mode==0 and remainder>q) or (mode==2 and remainder):q+=1
  exponent=(exponent-odd)//2
  if q==0x1000000:q>>=1;exponent+=1
  result.append(((exponent+127)<<23)|(q&0x7fffff))
 if precision and not (raised&~(control>>7)&3):raised|=32
 csr=control|raised;fault=bool(raised&~(control>>7)&63)
 assert csr==row['csr'] and fault==bool(row['code']) and (fault or result==row['output']),(row,result,csr,fault)
 checked+=1
assert checked==4096
summary=dict(status='integer square-root result and floating-state model matches characterization',checked=checked,raw_sha256=sha(source/'execute.stdout'),finding='Invalid/denormal precomputation faults suppress newly raised precision across the vector; old sticky flags remain. Positive finite binary32 square roots have normal finite outputs. Native Windows exception codes are not guest exception identities.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
