"""Audit canonical x87 image helpers and the independently isolated host pointer limit."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';p=base/'x87-serializer-probe-v3-pointer-isolation';s=read(p/'summary.json');raw=read(p/'execute.stdout')
assert s['checks']==5242880 and s['differences']==0 and s['full_tag_imports']==2097152 and s['control_word_imports']==65536 and s['AMD_policy_cases']==196608
assert s['host_pointer_loss_cases']+s['full_pointer_hardware_matches']==196608
for key,value in raw.items():assert s[key]==value
assert sha(p/'execute.stdout')==s['raw_sha256'] and sha(p/'fixture.exe')==s['fixture_sha256'] and sha(root/'native/semantics/x87_environment.h')==s['serializer_sha256']
layout=read(base/'x87-layout-probe-v1/summary.json');assert layout['control_cases']['fldcw_matches']==layout['control_cases']['fldenv_matches']==65536
assert sha(base/'x87-layout-probe-v1/execute.stdout')==layout['raw_sha256']
pointer=read(base/'x87-pointer-probe-v1/summary.json');groups=[json.loads(line) for line in (base/'x87-pointer-probe-v1/execute.stdout').read_text().splitlines()];assert pointer['groups']==groups and sha(base/'x87-pointer-probe-v1/execute.stdout')==pointer['raw_sha256']
assert all(g['other_pointer_changes']==0 and g['changed']==g['upper_halves_cleared'] for g in groups)
slow=[g for g in groups if g['delay_iterations']>1];assert sum(g['changed'] for g in slow)==1006 and sum(g['cases'] for g in slow)==1024
failures={}
for name in ['x87-serializer-probe-v1','x87-serializer-probe-v2-diagnostic']:
 data=read(base/name/'execute.stdout');assert data['differences']==1 and data['checks']==5046272;failures[name]=dict(observation=data,raw_sha256=sha(base/name/'execute.stdout'),diagnostic=(base/name/'execute.stderr').read_text(encoding='utf-8'))
assert '12:78/00 13:56/00 20:89/00 21:67/00' in failures['x87-serializer-probe-v2-diagnostic']['diagnostic']
runs={}
for suffix in ['x87-layout-probe-v1','x87-serializer-probe-v1','x87-serializer-probe-v2-diagnostic','x87-pointer-probe-v1','x87-serializer-probe-v3-pointer-isolation']:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']==('failed' if suffix in failures else 'pass')
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
accepted=root/'build/extended-semantics-v9-sqrt';assert sha(accepted/'amd64_avx.bc')==read(accepted/'identity.json')['semantics_sha256']
report=dict(status='canonical x87 image helper evidence passed within explicit profiles; no startup selectors added',serializer=s,layout=layout,host_pointer_probe=pointer,retained_failures=failures,runs=runs,source_sha256={p:sha(root/p) for p in ['native/semantics/x87_environment.h','native/semantics/x87_serializer_probe.cpp','native/semantics/x87_layout_probe.cpp','native/semantics/x87_pointer_probe.cpp','tools/x87_serializer_probe.py','tools/x87_layout_probe.py','tools/x87_pointer_probe.py']},primary_sources=['https://docs.amd.com/api/khub/documents/w13cmcpL4f9MCT4WPN6eDg/content','https://docs.amd.com/api/khub/documents/sfvvekC9mDflu6vd3R0NXA/content','https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-context'],source_access='AMD FXSAVE and environment text retrieved through the primary-source search index; direct AMD API PDF retrieval returns 404. Windows CONTEXT definition and installed SDK XSAVE_FORMAT are readable.',next_work=['Bind the tested image helpers to experimental instruction selectors with explicit full-span RAM access and waiting/alignment boundaries.','Integrate guest last-pointer segment metadata and the AMD conditional-pointer profile, without inferring it from the Intel host.','Normalize all FLDCW input bits and correct adjacent LDMXCSR/STMXCSR guest state isolation.','Complete coherent x87 memory conversion/arithmetic and MMX alias treatment before accepting startup semantics.'],limitations=['The 5,242,880 checks include 196,608 policy witnesses; AMD policy checks are documented byte-write expectations, not AMD execution.','One host upper-pointer truncation remains counted in the passing serializer run; it is accepted only if both pointer upper halves become zero and every other saved byte matches. Canonical 64-bit values are checked independently.','Delayed pointer imports show truncation with and without exception state and affinity pinning; this supports a host preservation limit but does not establish a particular Windows kernel instruction path.','The serializers are pure state-image helpers. No instruction selector, memory-fault implementation, game object, native link or game execution was added.','Sixteen-entry experimental x87 stack/control semantics remain v15; accepted startup semantics remain v9-sqrt. Native exception delivery, arithmetic, last-pointer metadata and MMX/x87 aliasing are open.'],compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-serializer-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],checks=s['checks'],host_pointer_loss_cases=s['host_pointer_loss_cases'],delayed_pointer_loss=1006,serializer_sha256=s['serializer_sha256']));print(json.dumps(read(out/'summary.json')),flush=True)
