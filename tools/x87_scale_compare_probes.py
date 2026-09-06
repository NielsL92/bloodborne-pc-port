"""Compare independent FSCALE setup paths, explicitly normalizing initial TOP."""
import itertools,json,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
a=Path(sys.argv[1]);b=Path(sys.argv[2]);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=False)
count=bad=0;examples=[]
with (a/'execute.stdout').open(encoding='utf-8') as fa,(b/'execute.stdout').open(encoding='utf-8') as fb:
 for first,second in itertools.zip_longest(fa,fb):
  assert first is not None and second is not None;x=json.loads(first);y=json.loads(second);count+=1
  same=all(x[k]==y[k] for k in ['form','type','pair','signs','control','input_c1','sig0','exp0','sig1','exp1'])
  same &= x['top']==0 and y['top']==6 and x['tags']==3 and y['tags']==192 and (x['status']&~0x3800)==(y['status']&~0x3800)
  if not same:
   bad+=1
   if len(examples)<8:examples.append(dict(first=x,second=y))
summary=dict(status='independent FSCALE setup comparison retained',cases=count,differing_cases=bad,examples=examples,first=str(a),second=str(b),first_raw_sha256=sha(a/'execute.stdout'),second_raw_sha256=sha(b/'execute.stdout'),normalization='Both instructions preserve their initial physical tags and TOP. FXRSTOR starts TOP=0/tags=3; two FLD80 loads start TOP=6/tags=192. Compare all other status bits and both raw logical operands exactly.',limitations='Authored Intel-host evidence only; no AMD Jaguar or game execution.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True);assert count==761856 and not bad
