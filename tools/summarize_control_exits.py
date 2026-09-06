"""Verify repeated LLVM control-exit evidence and publish the open boundary gate."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
base=root/'local/compiler-spike';current=base/'control-exit-inventory-v4-repeat';previous=base/'control-exit-inventory-v3-origins'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
s=read(current/'summary.json');assert s==read(previous/'summary.json')
assert s['objects']==386 and s['compiled_functions']==21282 and s['indirect_llvm_calls']==0
assert s['active_manifest_sha256']==sha(root/s['active_manifest'])
assert s['missing_block_pc_value_kinds']=={'load':4818}
assert s['error_semantic_origin_counts']=={'IDIVrdxrax':10,'DIVrdxrax':26,'IDIVedxeax':10,'COMISS':32,'COMISD':17,'DIVedxeax':10}
assert s['function_attribute_counts']==[dict(calling_convention=0,nounwind=False,noreturn=False,count=21282)]
for row in s['control_site_attribute_counts']:
 if row['callee'].startswith('__remill_'):assert row['nounwind'] and not row['noreturn'] and not row['is_invoke']
for name,digest in s['artifact_sha256'].items():assert sha(current/name)==digest==sha(previous/name)
for obj in read(current/'objects.json'):
 name=f"object-{obj['index']:04d}.json";assert sha(current/name)==obj['report_sha256']==sha(previous/name)
 folder=base/obj['source_batch']/obj['folder'];assert sha(folder/'function.bc')==obj['bitcode_sha256'] and sha(folder/'function.obj')==obj['object_sha256']
identity=read(root/'build/control-audit-v4-context/identity.json');assert sha(root/'build/control-audit-v4-context/control-audit.exe')==s['inspector_sha256']==identity['executable_sha256']
assert sha(root/'native/control_audit/main.cpp')==identity['source_sha256']
runs={}
for suffix in ['control-audit-build-v4-context','control-exit-inventory-v3-origins','control-exit-inventory-v4-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for file,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(file.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
paths=['external/remill/lib/BC/TraceLifter.cpp','external/remill/include/remill/Arch/Runtime/Operators.h','external/remill/lib/Arch/X86/Semantics/BINARY.cpp','external/remill/lib/Arch/X86/Semantics/SSE.cpp']
evidence=dict(status='complete retained-bitcode control-site census independently repeated; native exit contracts remain open',inventory=s,source_sha256={p:sha(root/p) for p in paths},runs=runs,attribution=dict(integer_division_error_sites=56,scalar_comparison_error_sites=49,method='Retained inlined semantic successor names, cross-checked with StopFailure uses in pinned BINARY.cpp/SSE.cpp. This identifies semantic families, not exact guest fault sites or hardware correctness.'),retained_failures=['control-audit-build-v1: LLVM 21 API/include mismatch; corrected in v2-api, raw compile diagnostics preserved.'],next_work=['Check COMISS/COMISD NaN, MXCSR, fault, flag and host-isolation behavior independently; current source is a concrete unresolved semantic lead.','Retain source instruction, expected continuation and exit reason in compiler/native boundary interfaces; an available target alone does not authorize a dispatch.','Establish nounwind-compatible native handling or deliberately change and validate compiler contracts before throwing/unwinding.','Then bind/import/link the complete object set and test explicit boundaries before declaring P3 passed.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/control-exits-evidence.json',evidence);write_json(out/'summary.json',dict(status=evidence['status'],objects=386,compiled_functions=21282,missing_block_ir_sites=4818,semantic_error_ir_sites=105,game_execution=False));print(json.dumps(read(out/'summary.json')),flush=True)
