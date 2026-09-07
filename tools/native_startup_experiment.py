"""Execute a bounded supplied-entry AOT probe with private NX data and exact stop assertions."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
from tools.native_load_format import bundle,expected
p=argparse.ArgumentParser();p.add_argument('contract',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();env=environment();steps=[]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
contract=read(a.contract/'contract.json');registry=ROOT/'local/runtime/registry-v7-memory-repeat';plan=ROOT/'local/runtime/loader-plan-v8-memory';identity=read(registry/'identity.json');assert contract['registry_identity']==sha(registry/'identity.json');assert contract['loader_plan_sha256']==sha(plan/'summary.json')
for name,digest in identity['files'].items():assert sha(registry/name)==digest
for name,digest in read(plan/'summary.json')['files'].items():assert sha(plan/name)==digest
objects=read(registry/'objects.json');targets=read(registry/'targets.json');imports=read(registry/'imports.json');assert len(objects)==386 and len(targets)==21282 and len(imports)==775
for obj in objects:assert sha(obj['path'])==obj['sha256']
rows=[dict(base=r['base'],size=r['mapped_size'],declared=r['declared_memory_size'],rights=r['native_rights'],initial=(plan/r['initial_file']).read_bytes()) for r in read(plan/'regions.json')];bases={r['module']:r['logical_base'] for r in read(plan/'modules.json')};relocations=[];guards=[]
for r in map(json.loads,(plan/'relocations.jsonl').read_text(encoding='utf-8').splitlines()):
 at=bases[r['module']]+r['offset']
 if r['value'] is None:guards.append(dict(base=at,size=8,identity=f"{r['module']}:{r['offset']:x}:{r['type']}"))
 else:relocations.append((at,r['value']))
# Reusable encoding/digest refactor must reproduce the preceding standalone loader evidence.
assert hashlib.sha256(bundle(rows,relocations,guards,contract['registry_identity'])).hexdigest()==read(ROOT/'local/runtime/load-v3-repeat/summary.json')['bundle_sha256'];assert expected(rows,relocations,guards)==read(ROOT/'local/runtime/load-v3-repeat/expected.json')
stack=bytearray(contract['stack_size']);params=bytearray(contract['parameter_size']);argv0=contract['parameter_base']+0x1000;initial_rsp=contract['stack_base']+len(stack)-24;assert initial_rsp%16==contract['initial_rsp_mod16'];struct.pack_into('<QQ',stack,len(stack)-24,contract['argc'],argv0);struct.pack_into('<IIQ',params,0,contract['argc'],0,argv0);struct.pack_into('<Q',params,272,contract['entry_pc']);name=contract['argv0'].encode('ascii')+bytes(1);params[0x1000:0x1000+len(name)]=name
for base,initial in [(contract['stack_base'],stack),(contract['parameter_base'],params)]:rows.append(dict(base=base,size=len(initial),declared=len(initial),rights=3,initial=initial))
image=bundle(rows,relocations,guards,contract['registry_identity']);(out/'startup.bin').write_bytes(image);expected_image=expected(rows,relocations,guards);write_json(out/'expected-image.json',expected_image)
manifest=dict(contract_sha256=sha(a.contract/'contract.json'),registry_identity=contract['registry_identity'],bundle_sha256=sha(out/'startup.bin'),expected_image=expected_image,initial_rsp=initial_rsp,entry_pc=contract['entry_pc'],parameter_base=contract['parameter_base'],exit_callback=contract['exit_callback_pc'],other_state='zeroed explicit probe context; no target FP/TLS profile',callback='native diagnostic process stop',expected_stop=contract['expected_stop']);write_json(out/'probe-manifest.json',manifest);trace_id=sha(out/'probe-manifest.json')
header=['#pragma once']
for key,value in dict(REGISTRY_ID=contract['registry_identity'],BUNDLE_SHA256=sha(out/'startup.bin'),TRACE_ID=trace_id,EXPECTED_IMAGE_SHA256=expected_image['sha256_unguarded']).items():header.append('static constexpr const char* '+key+'='+json.dumps(value)+';')
for key,value in dict(ENTRY_PC=contract['entry_pc'],INITIAL_RSP=initial_rsp,PARAMETERS=contract['parameter_base'],EXIT_CALLBACK_PC=contract['exit_callback_pc'],EXPECTED_MAPPED_BYTES=expected_image['mapped_bytes']).items():header.append(f'static constexpr uint64_t {key}={value}ULL;')
(out/'startup-config.h').write_text(chr(10).join(header)+chr(10),encoding='utf-8')
def run(name,argv,code=0,timeout=180):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=timeout)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==code,(name,r.returncode)
native=[]
for name in ['fault','memory','control','intrinsics','fp','sourced','loader','startup_fixture','registry']:
 source=registry/'registry.cpp' if name=='registry' else ROOT/'native/runtime'/(name+'.cpp');obj=out/(name+'.obj');native.append(obj);run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(ROOT/'native/runtime'),'/I'+str(out),'/c',source,'/Fo'+str(obj)])
run('numeric',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/c',ROOT/'native/semantics/x87_numeric.cpp','/Fo'+str(out/'numeric.obj')]);native.append(out/'numeric.obj');softfloat=ROOT/'build/softfloat-v2-repeat/softfloat.lib';builtins=LLVM/'lib/clang/21/lib/windows/clang_rt.builtins-x86_64.lib'
argv=['/nologo','/subsystem:console','/machine:x64',*[r['path'] for r in objects],*map(str,native),str(softfloat),str(builtins),'/out:'+str(out/'startup.exe'),'/INCREMENTAL:NO','/Brepro','/OPT:NOICF','/OPT:NOREF','/MAP:'+str(out/'startup.map')];(out/'link.rsp').write_text(chr(10).join(subprocess.list2cmdline([s]) for s in argv)+chr(10),encoding='utf-8');run('link',[LLVM/'bin/lld-link.exe','@'+str(out/'link.rsp')])
raw=(out/'startup.exe').read_bytes();nt=struct.unpack_from('<I',raw,0x3c)[0];assert raw[nt:nt+4]==b'PE'+bytes(2);count=struct.unpack_from('<H',raw,nt+6)[0];optional=nt+24;optional_size=struct.unpack_from('<H',raw,nt+20)[0];assert struct.unpack_from('<H',raw,optional)[0]==0x20b;image_base=struct.unpack_from('<Q',raw,optional+24)[0];executable=[]
for n in range(count):
 at=optional+optional_size+n*40;size,rva=struct.unpack_from('<II',raw,at+8);flags=struct.unpack_from('<I',raw,at+36)[0];assert not (flags&0x20000000 and flags&0x80000000)
 if flags&0x20000000:executable.append((image_base+rva,image_base+rva+size))
linked={}
for line in (out/'startup.map').read_text().splitlines():
 match=re.match(r'\s+[0-9a-fA-F]+:[0-9a-fA-F]+\s+sub_([0-9a-f]+)\s+([0-9a-fA-F]+)\s+',line)
 if match:
  pc,host=map(lambda value:int(value,16),match.groups());assert pc not in linked;linked[pc]=host
assert set(linked)=={r['pc'] for r in targets+imports} and len(set(linked.values()))==len(linked);assert all(any(start<=host<end for start,end in executable) for host in linked.values());write_json(out/'linked-roots.json',{str(pc):host for pc,host in sorted(linked.items())})
run('prepare',[out/'startup.exe','--prepare-only']);prepared=read(out/'prepare.stdout');assert prepared['trace_identity']==trace_id and prepared['private_image_sha256']==expected_image['sha256_unguarded'];run('invalid-mode',[out/'startup.exe','--run-game'],2)
# This is the first supplied-entry native AOT execution in the project. No original bytes execute.
run('entry',[out/'startup.exe','--probe-entry'],0xb0000008,timeout=10);assert read(out/'entry.stdout')==prepared;records=[json.loads(s) for s in (out/'entry.stderr').read_text(encoding='utf-8').splitlines()];assert len(records)==3;fault,active,guard=records;stop=contract['expected_stop'];assert fault['boundary']=='unresolved-relocation' and fault['reason']==8;assert int(fault['source'],16)==int(fault['pc'],16)==stop['source'];assert int(fault['address'],16)==stop['address'] and fault['width']==stop['width'];assert int(fault['rsp'],16)==initial_rsp-stop['rsp_decrement'] and int(fault['entry'],16)==contract['entry_pc'];assert fault['compilation_identity']==trace_id;assert int(active['active_import'],16)==stop['active_import'] and active['nid']==stop['nid'];assert guard['unresolved_identity']==stop['unresolved_identity'] and guard['completed_memory_operations']==stop['completed_memory_operations']
result=dict(status='bounded native AOT entry reaches the independently predicted unresolved canary-slot stop',trace_identity=trace_id,registry_identity=contract['registry_identity'],contract_sha256=sha(a.contract/'contract.json'),executable_sha256=sha(out/'startup.exe'),executable_bytes=(out/'startup.exe').stat().st_size,bundle_sha256=sha(out/'startup.bin'),private_image=expected_image,fault=fault,active_import=active,guard=guard,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Explicit probe State/arguments only; complete startup ABI, module initialization order, FP profile and TLS remain unimplemented.','Stops before atexit callback registration, constructor calls and main. The native exit callback is an explicit diagnostic stop.','The native entry and two supplied libc roots are compiled AOT code; source module copies remain NX data.','Eleven completed registered memory operations and the exact source/RSP are checked; this is not whole-game execution coverage.']);write_json(out/'summary.json',result);print(json.dumps(result),flush=True)
