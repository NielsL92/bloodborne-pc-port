"""Check explicit native UD2 declaration, exact fault address and no fallthrough."""
import copy,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);lifter=Path(sys.argv[2]).resolve();env=environment();base=0x100020000
valid=dict(roots=[base],instructions=[dict(address=base+pc,bytes=b) for pc,b in [(0,'83ff00'),(3,'743b'),(5,'b807000000'),(10,'c3'),(64,'b809000000'),(69,'0f0b')]],native_traps=[dict(address=base+69,kind='ud2')]);cases=[('explicit',valid,True)]
for name,change in [('undeclared',lambda d:d.pop('native_traps')),('duplicate',lambda d:d['native_traps'].append(d['native_traps'][0])),('wrong_kind',lambda d:d['native_traps'][0].update(kind='hlt')),('wrong_bytes',lambda d:d['native_traps'][0].update(address=base)),('dead_fallthrough',lambda d:d['instructions'].append(dict(address=base+71,bytes='c3')))]:
 d=copy.deepcopy(valid);change(d);cases.append((name,d,False))
steps=[]
def run(name,argv,code=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=120)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode,expected=code));write_json(out/'steps.json',steps);assert r.returncode==code,name
for name,data,accept in cases:
 folder=out/name;folder.mkdir();write_json(folder/'input.json',data)
 run(name,[lifter,folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json'],0 if accept else 2)
folder=out/'explicit';audit=json.loads((folder/'audit.json').read_text());assert audit['explicit_native_trap_addresses']==[base+69] and audit['semantic_instruction_count']==5
ir=(folder/'function.ll').read_text();assert '__bb_native_ud2' in ir and '__remill_error' not in ir
run('object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',out/'function.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/I'+str(ROOT/'external/remill/include'),'/c',ROOT/'native/sparse_lift/trap_fixture.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'function.obj','/Fe'+str(out/'fixture.exe')])
run('normal',[out/'fixture.exe']);run('fault',[out/'fixture.exe','fault'],74)
normal=json.loads((out/'normal.stdout').read_text());fault=json.loads((out/'fault.stdout').read_text());assert fault['fault_pc']==base+69
report=dict(status='explicit native trap checks pass',input_cases=6,normal=normal,fault=fault,audit=audit,lifter_sha256=sha(lifter),fixture_sha256=sha(out/'fixture.exe'),limitations='Authored conditional return and diagnostic process termination only. No hardware UD2/game CPU execution, PS4 exception delivery or native signal-handler dispatch implementation.')
write_json(out/'summary.json',report);print(json.dumps(dict(status=report['status'],input_cases=6,fault=fault)),flush=True)
