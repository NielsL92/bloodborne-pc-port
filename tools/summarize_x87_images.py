"""Audit authored x87 image bindings, runtime boundaries and preserved failures."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';sem=root/'build/extended-semantics-v18-x87-images';identity=read(sem/'identity.json')
assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for name,digest in identity['extension_sha256'].items():assert sha(Path(name))==digest
assert sha(root/'native/semantics/x87_environment.h')==identity['authored_header_sha256']['native/semantics/x87_environment.h']
observations={}
for name,cases in [('x87-image-bindings-v2-matrix',557864),('x87-stack-probe-v4-images',1499136),('x87-fault-probe-v8-images',720896)]:
 p=base/name;s=read(p/'summary.json');groups=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()]
 assert s['cases']==cases and s['differing_cases']==0 and sum(g['cases'] for g in groups)==cases
 assert s['groups']==groups and all(g['differing_cases']==0 and not any(g['differences'].values()) for g in groups)
 assert s['raw_sha256']==sha(p/'execute.stdout') and s['semantics_sha256']==identity['semantics_sha256'] and s['fixture_sha256']==sha(p/'fixture.exe')
 observations[name]=s
images=observations['x87-image-bindings-v2-matrix'];groups=images['groups']
assert sum(g['hardware_faults'] for g in groups)==161640 and sum(g['native_faults'] for g in groups)==161644 and sum(g['unsupported_spans'] for g in groups)==24
ir=(base/'x87-image-bindings-v2-matrix/function.ll').read_text(encoding='utf-8')
assert '__remill_fpu_' not in ir and 'declare dso_local' in ir
for service in ['check_span','image_policy','pointer_segments','set_pointer_segments','fault']:assert '@__bb_native_x87_'+service+'(' in ir
assert '@_ZN6bb_x879full_tags' not in ir
serializer=read(base/'x87-serializer-probe-v4-inline/summary.json')
assert serializer['checks']==5242880 and serializer['differences']==0 and serializer['serializer_sha256']==sha(root/'native/semantics/x87_environment.h')
assert serializer['host_pointer_loss_cases']+serializer['full_pointer_hardware_matches']==196608
assert serializer['raw_sha256']==sha(base/'x87-serializer-probe-v4-inline/execute.stdout')
runs={}
failed={'extended-semantics-v16-x87-images','x87-image-prepare-v1'}
for suffix in ['extended-semantics-v16-x87-images','extended-semantics-v17-x87-images','x87-image-prepare-v1','x87-image-semantics-v18','x87-image-prepare-v2','x87-image-bindings-v1','x87-image-bindings-v2-matrix','x87-stack-probe-v4-images','x87-fault-probe-v8-images','x87-serializer-probe-v4-inline']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix in failed else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
first=(root/'build/extended-semantics-v16-x87-images/compile.stderr').read_text(encoding='utf-8');second=(base/'x87-image-prepare-v1/lift.stderr').read_text(encoding='utf-8')
assert "'cstring' file not found" in first and 'Global is external' in second and 'full_tags' in second
accepted=root/'build/extended-semantics-v9-sqrt';assert sha(accepted/'amd64_avx.bc')==read(accepted/'identity.json')['semantics_sha256']
report=dict(status='experimental x87 image bindings and authored boundary checks passed; P3 startup gate remains open',images=images,regressions=observations,serializer_repeat=serializer,experimental_semantics_sha256=identity['semantics_sha256'],accepted_semantics_sha256=sha(accepted/'amd64_avx.bc'),runs=runs,retained_failures={'freestanding-header':dict(path='build/extended-semantics-v16-x87-images/compile.stderr',sha256=sha(root/'build/extended-semantics-v16-x87-images/compile.stderr'),resolution='Use compiler memory builtins in the pure header; standalone fixture includes cstring explicitly.'),'helper-linkage':dict(path='local/compiler-spike/x87-image-prepare-v1/lift.stderr',sha256=sha(base/'x87-image-prepare-v1/lift.stderr'),resolution='The pure full_tags helper survived optimization as an internal call. Existing MoveFunctionIntoModule only moves compiled roots; mandatory inlining keeps pure helper bodies in those roots. The driver was not weakened.')},source_sha256={p:sha(root/p) for p in ['native/semantics/X87_STATE.cpp.inc','native/semantics/X87_ENV.cpp.inc','native/semantics/x87_environment.h','native/semantics/x87_image_fixture.cpp','tools/x87_image_experiment.py','tools/build_extended_semantics.py']},limitations=['Authored AOT fixtures execute no game bytes. No new game object or startup execution coverage is claimed.','AMD conditional pointer and selector behavior is an explicit manual-based policy tested alongside Intel hardware results, not an AMD hardware observation.','Hardware comparisons use 32-bit last-pointer values to avoid the independently documented host upper-pointer preservation limit. The pure serializer repeats retain separate full-width checks and counted host-loss classification.','161640 hardware/native faults are compared; four additional native pending faults precede intentionally unsupported mapping checks. Twenty-four partial-span cases diagnose unsupported mapping, not a guest page fault.','Image selectors require stable fully mapped RAM while emitting bytes. Arbitrary mapping, concurrent protection changes, partial architectural writes, OSXSAVE/OSFXSR/FFXSR modes and console fault delivery are not implemented by this fixture.','Pointer segments are explicit fixture/runtime metadata. Other x87 producers and MMX aliasing still require coherent integration.','Experimental v18 is not promoted to startup. All x87 memory/arithmetic families, adjacent MXCSR host leakage and other P3 control/service contracts remain open.'],compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-image-evidence.json',report);summary=dict(status=report['status'],image_cases=images['cases'],hardware_faults=161640,additional_native_pending_cases=4,unsupported_mapping_cases=24,experimental_semantics_sha256=identity['semantics_sha256']);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
