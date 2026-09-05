"""Audit isolated BMI semantics, native UD2 boundaries and exact recompilation delta."""
import collections,hashlib,json,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();base=root/'local/compiler-spike/startup-batch-all-v1';a=root/'local/compiler-spike/startup-bmi-trap-recompile-v1';b=root/'local/compiler-spike/startup-bmi-trap-recompile-v2-repeat'
prior=json.loads((base/'results.json').read_text());left=json.loads((a/'results.json').read_text());right=json.loads((b/'results.json').read_text());assert len(left)==len(right)==41
old_compiled={(r['module'],pc) for r in prior if r['status']=='object_built' for pc in r['entries']};rejected={(r['module'],pc) for r in prior if r['status']!='object_built' for pc in r['entries']}
roots={pc:r['folder'] for r in prior if r['status']=='object_built' for pc in r['compiled_roots']};new_units=set();traps=set();objects=[]
assert {(r['module'],pc) for r in right for pc in r['entries']}==rejected
for x,y in zip(left,right,strict=True):
 assert (x['module'],x['entries'],x['status'],x['input_sha256'])==(y['module'],y['entries'],y['status'],y['input_sha256'])
 if y['status']!='object_built':continue
 p=b/y['folder'];assert x['object_sha256']==y['object_sha256']==sha(p/'function.obj');assert sha(a/x['folder']/'audit.json')==sha(p/'audit.json')
 audit=json.loads((p/'audit.json').read_text());data=json.loads((p/'input.json').read_text());assert set(audit['decoded_addresses'])=={i['address'] for i in data['instructions']}
 assert set(audit['explicit_native_trap_addresses'])=={r['address'] for r in data.get('native_traps',[])}
 assert audit['semantic_instruction_count']+len(audit['explicit_native_trap_addresses'])==len(data['instructions'])
 for pc in audit['compiled_roots']:assert pc not in roots;roots[pc]=y['folder']
 traps.update(audit['explicit_native_trap_addresses']);new_units.update((y['module'],pc) for pc in y['entries'])
 objects.append(dict(folder=y['folder'],module=y['module'],entries=y['entries'],object_sha256=y['object_sha256'],audit_sha256=sha(p/'audit.json'),native_traps=audit['explicit_native_trap_addresses'],external_declarations=y['external_declarations']))
assert len(new_units)==14 and len(objects)==7 and len(traps)==16 and not new_units&old_compiled
sem=json.loads((root/'build/extended-semantics-v1/identity.json').read_text());assert sha(root/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc')==sem['original_semantics_sha256'];assert sha(root/'build/extended-semantics-v1/amd64_avx.bc')==sem['semantics_sha256']
for path,digest in sem['original_source_sha256'].items():assert sha(root/path)==digest
for path,digest in sem['linked_bitcode_sha256'].items():assert sha(path)==digest
bmi=json.loads((root/'local/compiler-spike/bmi-semantics-v2/summary.json').read_text());trap=json.loads((root/'local/compiler-spike/sparse-trap-v1/summary.json').read_text());sparse=json.loads((root/'local/compiler-spike/sparse-checks-v5/summary.json').read_text())
assert bmi['result']['aot_cases']==34816 and sparse['native']['aot_cases']==8192 and trap['input_cases']==6 and trap['fault']['fault_pc']==0x100020045
runs={}
for suffix in ('build-extended-semantics-v1','build-sparse-lift-v4','build-sparse-lift-v5','bmi-semantics-checks-v1','bmi-semantics-checks-v2','sparse-lift-checks-v5','sparse-trap-checks-v1','startup-bmi-recompile-v1','startup-bmi-trap-recompile-v1','startup-bmi-trap-recompile-v2-repeat'):
 name='20260905-p3-'+suffix;p=root/'local/runs'/name;m=json.loads((p/'manifest.json').read_text());expected='failed' if suffix.startswith('startup-') else 'pass';assert m['status']==expected
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],elapsed_seconds=m['elapsed_seconds'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'))
report=dict(status='BMI and explicit UD2 compilation evidence pass; P3 open',directory=b.relative_to(root).as_posix(),summary=json.loads((b/'summary.json').read_text()),new_compiled_entries=len(new_units),combined_compiled_entries=len(old_compiled|new_units),remaining_compiler_rejections=34,remaining_quarantined_manifests=8,remaining_constructor_rejections=[dict(ordinal=13655,entry=0x10326c0),dict(ordinal=15621,entry=0x28772a0)],duplicate_logical_roots=0,byte_identical_repeat=True,objects=objects,semantic_module_sha256=sem['semantics_sha256'],original_semantics_unchanged=True,bmi_checks=bmi,trap_checks=trap,sparse_authored_cases=8192,runs=runs,limitations='Only authored BMI/conditional-trap code executed. Game-derived objects retain explicit service/control/exception dependencies and were not linked or executed. UD2 reports the faulting logical PC and terminates through a dedicated native boundary; PS4 exception delivery is not implemented. AF/PF outputs are undefined and excluded from BMI equality.',native_game_boot=False,native_port_playable=False)
write_json(root/'reports/bmi-trap-evidence.json',report)
print(json.dumps(dict(status=report['status'],new_entries=14,combined_compiled_entries=21118,remaining_compiler_rejections=34,explicit_native_traps=16,byte_identical_repeat=True)),flush=True)
