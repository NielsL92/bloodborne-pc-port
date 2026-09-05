"""Adversarial sparse input checks and an authored AOT branch/entry contract."""
import copy,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import environment,LLVM
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
lifter=Path(sys.argv[2]).resolve();env=environment();base=0x100000200
rows=[(0,'83ff00'),(3,'753b'),(5,'b807000000'),(10,'c3'),(64,'b809000000'),(69,'c3'),(1024,'b82a000000'),(1029,'c3')]
valid=dict(roots=[base,base+1024],instructions=[dict(address=base+a,bytes=b) for a,b in rows])
cases=[('valid_sparse',valid,True)]
for name,edit in [
 ('missing_root',lambda v:v.update(roots=[base])),
 ('duplicate_root',lambda v:v['roots'].append(base)),
 ('duplicate_instruction',lambda v:v['instructions'].append(v['instructions'][0].copy())),
 ('overlapping_instruction',lambda v:v['instructions'].append(dict(address=base+1,bytes='90'))),
 ('wrong_instruction_boundary',lambda v:v['instructions'].__setitem__(0,dict(address=base,bytes='83ff0075'))),
 ('interior_branch',lambda v:v['instructions'].__setitem__(1,dict(address=base+3,bytes='7501'))),
 ('invalid_hex',lambda v:v['instructions'].__setitem__(0,dict(address=base,bytes='zz'))),
 ('unmapped_root',lambda v:v['roots'].append(base+100)),
]:
 v=copy.deepcopy(valid);edit(v);cases.append((name,v,False))
# A real unresolved path must remain an explicit missing-block boundary.
cases.append(('explicit_missing',dict(roots=[base],instructions=[dict(address=base,bytes='e9fb010000')]),True))
results=[]
def run(cmd,folder,step):
 with (folder/(step+'.stdout')).open('wb') as o,(folder/(step+'.stderr')).open('wb') as e:r=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=120)
 return r.returncode
for name,data,accept in cases:
 folder=out/name;folder.mkdir();write_json(folder/'input.json',data)
 code=run([lifter,folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json'],folder,'lift')
 assert (code==0)==accept,(name,code)
 record=dict(case=name,exit_code=code,expected_accept=accept,input_sha256=sha(folder/'input.json'))
 if accept:
  audit=json.loads((folder/'audit.json').read_text());assert not audit['unvisited_manifest_instructions']
  assert audit['input_instructions']==len(data['instructions']);assert len(audit['decoded_addresses'])==len(data['instructions'])
  assert audit['missing_instruction_starts']==([base+512] if name=='explicit_missing' else [])
  record['audit']=audit
 results.append(record)
folder=out/'valid_sparse'
assert run([LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',folder/'function.obj'],folder,'object')==0
cmd=[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/arch:AVX2','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/Iexternal/remill/include','/c','native/sparse_lift/fixture.cpp',f'/Fo{folder}/fixture.obj']
assert run(cmd,folder,'harness')==0
assert run([LLVM/'bin/clang-cl.exe','/nologo',folder/'fixture.obj',folder/'function.obj',f'/Fe{folder}/fixture.exe'],folder,'link')==0
assert run([folder.resolve()/'fixture.exe'],folder,'execute')==0
native=json.loads((folder/'execute.stdout').read_text());assert native['aot_cases']==8192
report=dict(status='sparse input and authored AOT checks pass',lifter_sha256=sha(lifter),input_cases=results,native=native,
 object_sha256=sha(folder/'function.obj'),limitations='Authored branch, independent entry and logical return checks only. No supplied game CPU execution or game exception-runtime validation.')
write_json(out/'summary.json',report);print(json.dumps(dict(status=report['status'],input_cases=len(results),native=native)),flush=True)
