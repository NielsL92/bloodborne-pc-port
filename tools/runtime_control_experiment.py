"""Link authored AOT roots to checked native memory/control/import gateways."""
import argparse,json,struct,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[];pc=0x1000c0000
call=lambda source,target:'e8'+struct.pack('<i',target-source-5).hex()
body=[(0,call(pc,pc+64)),(5,'eb19'),(64,'b86f000000'),(69,'c3'),(0x100,call(pc+0x100,pc+0x2000)),(0x105,'c3'),(0x200,call(pc+0x200,pc+0x2010)),(0x205,'c3'),(0x300,'ffd1'),(0x302,'c3'),(0x400,'ffe1'),(0x500,call(pc+0x500,pc+64)),(0x600,call(pc+0x600,pc+0x640)),(0x640,'488304241b'),(0x645,'c3'),(0x700,'0f0b'),(0x800,'cc'),(0x801,'c3'),(0x900,'0fa2'),(0x902,'c3')]
source_roots=[pc+v for v in [0,64,0x100,0x200,0x300,0x400,0x500,0x600,0x640,0x700,0x800,0x900]];target_roots=[pc+32,pc+0x620];all_roots=sorted(source_roots+target_roots)
source=dict(roots=source_roots,instructions=[dict(address=pc+offset,bytes=code) for offset,code in body],return_contracts=[dict(address=pc+0x500,expected_next_pc=pc+0x505,kind='no-normal-return',provenance='authored runtime nonreturn assertion')],native_traps=[dict(address=pc+0x700,kind='ud2')]);target=dict(roots=target_roots,instructions=[dict(address=pc+32,bytes='01f8'),dict(address=pc+34,bytes='c3'),dict(address=pc+0x620,bytes='c3')])
header=[f'extern "C" Memory* sub_{value:x}(State*,uint64_t,Memory*);' for value in all_roots];header+=['#define BB_RUNTIME_TARGETS {'+','.join('{'+f'{value}ULL,sub_{value:x}'+'}' for value in all_roots)+'}'];(out/'runtime-entries.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')
def run(name,argv,expected=0):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==expected,(name,r.returncode)
objects=[]
for label,data in [('source',source),('target',target)]:
 folder=out/label;folder.mkdir();write_json(folder/'input.json',data);run(label+'-lift',[a.lifter.resolve(),folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json',a.semantics.resolve()]);obj=folder/'function.obj';run(label+'-object',[LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',obj]);objects.append(obj)
for name in ['fault','memory','control','intrinsics','control_fixture']:
 obj=out/(name+'.obj');objects.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(out),'/c',ROOT/'native/runtime'/(name+'.cpp'),'/Fo'+str(obj)])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',*objects,'/Fe'+str(out/'fixture.exe')]);run('positive',[out/'fixture.exe','positive']);positive=json.loads((out/'positive.stdout').read_text());assert positive['aot_cases']==20480;negative=[]
for mode,reason,boundary in [('bad-source',30,'unregistered-source-transfer'),('bad-request',29,'block-transfer-target'),('bad-return',1,'control-return'),('nonreturn',2,'control-return'),('unknown-target',27,'unknown-compiled-target'),('unimplemented-import',25,'unimplemented-import'),('ud2',34,'ud2'),('async',32,'unimplemented-async-hypercall'),('sync',33,'unimplemented-sync-hypercall')]:
 run(mode,[out/'fixture.exe',mode],0xb0000000|reason);records=[json.loads(line) for line in (out/(mode+'.stderr')).read_text().splitlines()];r=records[0];assert r['reason']==reason and r['boundary']==boundary
 if mode=='bad-return':assert int(r['source'],16)==pc+0x600 and int(r['actual'],16)==pc+0x620 and int(r['wanted'],16)==pc+0x605
 if mode=='nonreturn':assert int(r['source'],16)==pc+0x500 and int(r['actual'],16)==int(r['wanted'],16)==pc+0x505
 if mode=='unimplemented-import':assert len(records)==2 and records[1]['nid']=='authored-native'
 negative.append(dict(mode=mode,reason=reason,boundary=boundary))
run('bad-table',[out/'fixture.exe','bad-table']);assert json.loads((out/'bad-table.stdout').read_text())['status']=='setup-rejected'
summary=dict(status='authored AOT native control/memory/import boundary checks pass',positive=positive,negative=negative,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),source_sha256={str(p):sha(p) for p in sorted((ROOT/'native/runtime').glob('*')) if p.is_file()},limitations='Authored AOT only. Imported native arithmetic and compiled-export binding are fixture services; real service ABIs, guest exceptions/nonlocal transfers, full linkage and game startup remain open.');write_json(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],aot_cases=20480,negative_cases=len(negative),setup_rejections=1)),flush=True)
