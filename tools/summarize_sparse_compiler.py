"""Audit sparse compilation and authored execution; preserve separate static/runtime claims."""
import collections,json,sqlite3,zipfile,hashlib,struct
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();a=root/'local/compiler-spike/sparse-manifest-v4';b=root/'local/compiler-spike/sparse-manifest-v5-repeat'
summary=json.loads((b/'summary.json').read_text());assert summary['results']=={'object_built':12};assert summary['instructions']==1517 and summary['roots']==46
left=json.loads((a/'results.json').read_text());right=json.loads((b/'results.json').read_text());assert len(left)==len(right)==12
units=[];global_roots=collections.Counter();missing=[]
db=sqlite3.connect('file:local/cfg/startup-recovery-v7-repeat/analysis.sqlite?mode=ro',uri=True)
for x,y in zip(left,right,strict=True):
 assert (x['module_sha256'],x['entry'])==(y['module_sha256'],y['entry'])
 assert x['object_sha256']==y['object_sha256']==sha(b/y['folder']/'function.obj')
 assert struct.unpack_from('<I',(b/y['folder']/'function.obj').read_bytes(),4)[0]==0
 assert sha(a/x['folder']/'audit.json')==sha(b/y['folder']/'audit.json')
 assert x['input_sha256']==y['input_sha256']==sha(b/y['folder']/'input.json')
 folder=b/y['folder'];unit=json.loads((folder/'manifest.json').read_text());audit=json.loads((folder/'audit.json').read_text())
 rows=db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(y['module_sha256'],y['entry'])).fetchall()
 assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()==unit['instruction_set_sha256']
 assert {r[0]+0x100000000 for r in rows}==set(audit['decoded_addresses']);assert not audit['unvisited_manifest_instructions']
 assert all(z['classification']!='unclassified missing path' for z in y['missing_boundaries'])
 global_roots.update((y['module_sha256'],pc-0x100000000) for pc in audit['compiled_roots'])
 missing.extend(dict(module=y['module_sha256'],entry=y['entry'],**z) for z in y['missing_boundaries'])
 units.append(dict(module=y['module_sha256'],entry=y['entry'],instructions=y['instructions'],roots=y['roots'],input_bytes=y['instruction_bytes'],omitted_gap_bytes=y['analysis_span']-y['instruction_bytes'],object_bytes=y['object_bytes'],object_sha256=y['object_sha256'],input_sha256=y['input_sha256'],audit_sha256=sha(folder/'audit.json'),cpu_boundaries=y['unresolved_cpu_boundaries']))
build=json.loads((root/'build/sparse-lift-v3/identity.json').read_text());assert sha(root/'build/sparse-lift-v3/bb-sparse-lift.exe')==build['executable_sha256'];assert build['driver_source_sha256']==sha(root/'native/sparse_lift/main.cpp')
for path,digest in build['linked_library_sha256'].items():assert sha(path)==digest,path
old=json.loads((root/'local/compiler-spike/startup-manifest-v1/identity.json').read_text());assert old['lifter_sha256']==sha(root/'build/remill/bin/lift/remill-lift-21.exe')
checks=json.loads((root/'local/compiler-spike/sparse-checks-v4/summary.json').read_text());assert checks['native']['aot_cases']==8192 and not checks['native']['original_code_execution'];assert checks['lifter_sha256']==build['executable_sha256']
runs={}
for suffix in ('build-sparse-lift-v1','build-sparse-lift-v2','build-sparse-lift-v3','sparse-lift-checks-v1','sparse-lift-checks-v2','sparse-lift-checks-v3','sparse-lift-checks-v4','sparse-compiler-evidence-v1','sparse-manifest-compile-v1','sparse-manifest-compile-v2','sparse-manifest-compile-v3-repeat','sparse-manifest-compile-v4','sparse-manifest-compile-v5-repeat'):
 name='20260905-p3-'+suffix;folder=root/'local/runs'/name;m=json.loads((folder/'manifest.json').read_text());expected='failed' if suffix in ('build-sparse-lift-v1','sparse-lift-checks-v1','sparse-compiler-evidence-v1') else 'pass';assert m['status']==expected
 with zipfile.ZipFile(folder/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],elapsed_seconds=m['elapsed_seconds'],source_archive_sha256=sha(folder/'sources.zip'))
timestamp_differences=[]
for x in left:
 first=(root/'local/compiler-spike/sparse-manifest-v2'/x['folder']/'function.obj').read_bytes();second=(root/'local/compiler-spike/sparse-manifest-v3-repeat'/x['folder']/'function.obj').read_bytes()
 assert len(first)==len(second) and first[:4]==second[:4] and first[8:]==second[8:]
 timestamp_differences.append(dict(entry=x['entry'],first=struct.unpack_from('<I',first,4)[0],second=struct.unpack_from('<I',second,4)[0],all_other_bytes_identical=True))
identity=json.loads((b/'identity.json').read_text());assert identity['semantics_sha256']==sha(root/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc');assert '-mno-incremental-linker-compatible' in identity['object_flags']
report=dict(status='sparse compiler evidence consistency pass; P3 gate open',current_directory=b.relative_to(root).as_posix(),summary=summary,
 driver=dict(path='build/sparse-lift-v3/bb-sparse-lift.exe',identity_sha256=sha(root/'build/sparse-lift-v3/identity.json'),executable_sha256=build['executable_sha256'],semantics_sha256=sha(root/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc'),original_lifter_unchanged=True,linked_libraries_unchanged=True),
 authored_checks=dict(path='local/compiler-spike/sparse-checks-v4/summary.json',sha256=sha(root/'local/compiler-spike/sparse-checks-v4/summary.json'),input_cases=len(checks['input_cases']),native=checks['native']),
 units=units,missing_boundaries=missing,duplicate_roots=[dict(module=h,rva=pc,copies=n) for (h,pc),n in global_roots.items() if n>1],
 determinism=dict(repeat_objects_byte_identical=True,coff_timestamp=0,object_flags=identity['object_flags'],previous_timestamp_only_differences=timestamp_differences),
 root_reduction=dict(initial=json.loads((root/'local/compiler-spike/sparse-manifest-v1/summary.json').read_text()),current=summary),runs=runs,
 retained_failures=[dict(run='20260905-p3-sparse-compiler-evidence-v1',reason='Raw v2/v3 object equality failed. All twelve differed only in the COFF timestamp bytes at offsets 4..7. The deterministic compiler flag fixes new emissions; original files remain preserved.'),dict(run='20260905-p3-build-sparse-lift-v1',reason='Separate TraceLifter compilation needed external/remill/lib/BC for its private InstructionLifter.h; corrected include path, original Remill untouched.'),dict(run='20260905-p3-sparse-lift-checks-v1',reason='All ten input checks passed; clang-cl rejected combined source/object compilation with /Fo. Separate harness compile/link fixed it; no execution occurred in that failed run.')],
 limitations='Instruction census requires matching Remill boundaries and successful semantic lifting, but is not execution coverage. All game-derived objects retain native control/service dependencies and were not linked or executed. Authored AOT checks exercise branch, independent entry and logical return only.',
 gate='P3 still open: sparse input blocker resolved for all twelve retained bodies; the separate disputed entry, nine startup fence findings, 9029 indirect-call records, 430 indirect-jump records and native callback/exception/service/runtime contracts remain open.',native_game_boot=False,native_port_playable=False)
write_json(root/'reports/sparse-compiler-evidence.json',report)
print(json.dumps(dict(status=report['status'],objects=12,instructions=1517,roots=46,object_bytes=summary['objects_bytes'],missing_paths=len(missing),duplicate_roots=len(report['duplicate_roots']),authored_aot_cases=8192)),flush=True)
