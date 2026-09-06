"""Link all startup objects, then run only a host registry validator."""
import argparse,json,re,subprocess,struct
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('registry',type=Path);p.add_argument('library',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve();registry=a.registry.resolve();env=environment();steps=[]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
identity=read(registry/'identity.json');summary=read(registry/'summary.json');assert sha(registry/'registry.cpp')==summary['registry_sha256'];assert sha(registry/'identity.json')==summary['identity_sha256']
for name,digest in identity['files'].items():assert sha(registry/name)==digest
objects=read(registry/'objects.json');targets=read(registry/'targets.json');imports=read(registry/'imports.json')
for obj in objects:assert sha(obj['path'])==obj['sha256']
def run(name,argv,expected=0,timeout=180):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=timeout)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert (r.returncode&0xffffffff)==expected,(name,r.returncode)
native=[]
for name in ['fault','memory','control','intrinsics','fp','registry_main','registry']:
 source=registry/'registry.cpp' if name=='registry' else ROOT/'native/runtime'/(name+'.cpp');obj=out/(name+'.obj');native.append(obj)
 run(name,[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/DADDRESS_SIZE_BITS=64','/DHAS_FEATURE_AVX=1','/DHAS_FEATURE_AVX512=0','/clang:-mlong-double-80','/clang:-mno-avx','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/remill/include'),'/I'+str(ROOT/'native/runtime'),'/c',source,'/Fo'+str(obj)])
run('numeric',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-incremental-linker-compatible','/I'+str(ROOT/'external/SoftFloat-3e/source/include'),'/c',ROOT/'native/semantics/x87_numeric.cpp','/Fo'+str(out/'numeric.obj')]);native.append(out/'numeric.obj');builtins=LLVM/'lib/clang/21/lib/windows/clang_rt.builtins-x86_64.lib'
argv=['/nologo','/subsystem:console','/machine:x64',*[r['path'] for r in objects],*map(str,native),str(a.library.resolve()),str(builtins),'/out:'+str(out/'registry.exe'),'/INCREMENTAL:NO','/Brepro','/OPT:NOICF','/OPT:NOREF','/MAP:'+str(out/'registry.map')]
# A structured response file avoids the Windows command-line length limit.
(out/'link.rsp').write_text(chr(10).join(subprocess.list2cmdline([s]) for s in argv)+chr(10),encoding='utf-8');run('link',[LLVM/'bin/lld-link.exe','@'+str(out/'link.rsp')])
run('validate',[out/'registry.exe','--validate-only']);result=read(out/'validate.stdout');assert result['compiled_roots']==len(targets) and result['imports']==len(imports) and result['identity']==summary['identity_sha256'];assert not result['game_entry_called'] and not result['guest_mappings_created'] and not result['fp_profile_selected']
run('reject-entry',[out/'registry.exe','--run-game'],2)
negative=[]
for index,row in enumerate(imports):
 if row['compiled_export']:continue
 name=f'native-import-{index:03d}';run(name,[out/'registry.exe','--probe-native-import',index],0xb0000019);records=[json.loads(line) for line in (out/(name+'.stderr')).read_text().splitlines()];assert len(records)==2;fault,imp=records;assert fault['boundary']=='unimplemented-import' and fault['compilation_identity']==summary['identity_sha256'];assert int(fault['pc'],16)==row['pc'] and int(imp['active_import'],16)==row['pc'];assert all(imp[k]==row[k] for k in ['nid','library','module']);negative.append(dict(index=index,pc=row['pc'],boundary=fault['boundary'],nid=row['nid']))
run('unknown-target',[out/'registry.exe','--probe-unknown'],0xb000001b);unknown=read(out/'unknown-target.stderr');assert unknown['boundary']=='unknown-compiled-target' and int(unknown['actual'],16)==0;write_json(out/'native-import-stops.json',negative)

map_text=(out/'registry.map').read_text();entries={}
for line in map_text.splitlines():
 match=re.match(r'\s+[0-9a-fA-F]+:[0-9a-fA-F]+\s+(sub_([0-9a-f]+))\s+([0-9a-fA-F]+)\s+(?:f\s+)?\S+',line)
 if match:
  symbol,logical,host=match.groups();assert symbol not in entries;entries[symbol]=dict(logical_pc=int(logical,16),host_address=int(host,16))
expected={f'sub_{r["pc"]:x}' for r in targets+imports};assert set(entries)==expected,dict(missing=sorted(expected-set(entries))[:20],extra=sorted(set(entries)-expected)[:20]);assert len({r['host_address'] for r in entries.values()})==len(entries)
raw=(out/'registry.exe').read_bytes();nt=struct.unpack_from('<I',raw,0x3c)[0];assert raw[nt:nt+4]==b'PE'+bytes(2);sections=struct.unpack_from('<H',raw,nt+6)[0];optional_size=struct.unpack_from('<H',raw,nt+20)[0];optional=nt+24;assert struct.unpack_from('<H',raw,optional)[0]==0x20b;image_base=struct.unpack_from('<Q',raw,optional+24)[0];executable=[]
for index in range(sections):
 at=optional+optional_size+index*40;size,rva=struct.unpack_from('<II',raw,at+8);flags=struct.unpack_from('<I',raw,at+36)[0];assert not (flags&0x20000000 and flags&0x80000000),'writable executable PE section'
 if flags&0x20000000:executable.append((image_base+rva,image_base+rva+size))
assert all(any(start<=r['host_address']<end for start,end in executable) for r in entries.values()),'linked root outside native executable sections'
write_json(out/'linked-addresses.json',entries);run('pe',[LLVM/'bin/llvm-readobj.exe','--file-headers','--sections','--coff-imports',out/'registry.exe']);pe=(out/'pe.stdout').read_text();assert 'COFF-x86-64' in pe
result=dict(status='complete startup objects linked; host-only registry validated',registry_identity_sha256=summary['identity_sha256'],objects=len(objects),linked_game_roots=len(targets),linked_import_gateways=len(imports),tested_unimplemented_import_stops=len(negative),unknown_target_stops=1,runtime_validation=result,executable_sha256=sha(out/'registry.exe'),executable_bytes=(out/'registry.exe').stat().st_size,linked_addresses_sha256=sha(out/'linked-addresses.json'),native_objects={p.name:sha(p) for p in native},softfloat_sha256=sha(a.library),builtins_sha256=sha(builtins),game_execution=False,limitations='Host-only table validation. No game entry, game mappings, FP profile selection, real services, guest exceptions/nonlocal recovery, boot or gameplay. Export binding is conditional on exact module identity and loader/initialization assumptions.')
write_json(out/'summary.json',result);print(json.dumps(result),flush=True)
