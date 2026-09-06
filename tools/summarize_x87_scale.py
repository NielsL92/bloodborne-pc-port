"""Audit exact FSCALE numeric, instruction and independent setup evidence."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';sem=root/'build/extended-semantics-v31-scale';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in identity['authored_header_sha256'].items():assert sha(root/path)==digest
observations={}
for name,count,bad in [('x87-scale-numeric-v1',761856,256),('x87-scale-numeric-v2-zero',761856,0),('x87-scale-numeric-v3-edges',2021632,0),('x87-scale-bindings-v1',2809856,0),('x87-scale-bindings-v2-repeat',2809856,0),('x87-arithmetic-bindings-v4-scale',8052736,0)]:
 p=base/name;s=read(p/'summary.json');rows=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert s['groups']==rows and s['cases']==count and s['differing_cases']==bad and s['raw_sha256']==sha(p/'execute.stdout')
 if 'bindings' in name:assert s['semantics_sha256']==identity['semantics_sha256']
 assert s['library_sha256']==sha(root/'build/softfloat-v2-repeat/softfloat.lib');observations[name]=s
scale=observations['x87-scale-bindings-v2-repeat'];groups=scale['groups'];assert len(groups)==6 and groups[0]==dict(form='numeric-scope',cases=1048576,differing_cases=0)
assert all(not any(g['differences'].values()) and not g['pointer_observation_differences'] and not g['opcode_observation_differences'] for g in groups[1:])
counts={key:sum(g.get(key,0) for g in groups) for key in ['hardware_faults','native_faults','unsupported_cases']};assert counts==dict(hardware_faults=349046,native_faults=349046,unsupported_cases=0)
repeat={}
for name in ['function.bc','function.obj','numeric.obj','execute.stdout']:
 a=base/'x87-scale-bindings-v1'/name;b=base/'x87-scale-bindings-v2-repeat'/name;assert a.read_bytes()==b.read_bytes();repeat[name]=sha(a)
independent={}
for name in ['x87-scale-probe-v1','x87-scale-probe-v2-load-input','x87-scale-probe-v3-load-repeat']:
 p=base/name;s=read(p/'summary.json');assert s['cases']==761856 and s['raw_sha256']==sha(p/'execute.stdout');independent[name]=s
assert (base/'x87-scale-probe-v2-load-input/execute.stdout').read_bytes()==(base/'x87-scale-probe-v3-load-repeat/execute.stdout').read_bytes()
assert all(g['top_changed']==0 for g in independent['x87-scale-probe-v3-load-repeat']['groups'][0]['unmasked_by_flags'].values())
comparison=read(base/'x87-scale-probes-comparison-v1/summary.json');assert comparison['cases']==761856 and not comparison['differing_cases'] and comparison['first_raw_sha256']==independent['x87-scale-probe-v1']['raw_sha256'] and comparison['second_raw_sha256']==independent['x87-scale-probe-v2-load-input']['raw_sha256']
controls={};pc_cases=0;zero_observations=[]
for line in (base/'x87-scale-probe-v1/execute.stdout').open(encoding='utf-8'):
 r=json.loads(line);cw=r['control'];pc=(cw>>8)&3;key=(r['type'],r['pair'],r['signs'],cw&~0x300,r['input_c1']);value=tuple(r[k] for k in ['status','tags','sig0','exp0','sig1','exp1'])
 if pc==0:controls[key]=value
 else:assert controls[key]==value;pc_cases+=1
 assert r['top']==0 and r['tags']==3
 if r['type'] in [5,6] and r['pair'] in [0,22,24,29] and r['signs']==0 and cw==0x36f and not r['input_c1']:
  assert (r['status']&63)==(2 if r['pair']==0 else 18);zero_observations.append(r)
assert pc_cases==571392 and len(zero_observations)==8
runs={}
for suffix in ['x87-scale-probe-v1','x87-scale-numeric-v1','x87-scale-probe-v2-load-input','x87-scale-probes-comparison-v1','x87-scale-numeric-v2-zero','x87-scale-numeric-v3-edges','x87-scale-semantics-v31','x87-scale-bindings-v1','x87-scale-bindings-v2-repeat','x87-arithmetic-bindings-v4-scale','x87-scale-probe-v3-load-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix=='x87-scale-numeric-v1' else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
  if suffix=='x87-scale-bindings-v2-repeat':
   for path in ['native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h','native/semantics/x87_numeric_scope_fixture.cpp','native/semantics/X87_SCALE.cpp.inc','native/semantics/x87_scale_fixture.cpp']:assert z.read(path)==(root/path).read_bytes()
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
ir=(base/'x87-scale-bindings-v2-repeat/function.ll').read_text(encoding='utf-8');assert '__remill_fpu_' not in ir and 'x86_fp80' not in ir
for name in ['__bb_x87_scale','__bb_native_x87_fault','__bb_native_x87_record_instruction']:assert '@'+name in ir
report=dict(status='experimental native FSCALE checks pass; startup integration and P3 remain open',scale=scale,numeric=observations['x87-scale-numeric-v3-edges'],observations=observations,independent_hardware=independent,independent_setup_comparison=comparison,precision_independence_pairs=pc_cases,zero_scale_observations=zero_observations,counts=counts,reproducible_artifacts=repeat,runs=runs,source_sha256={path:sha(root/path) for path in ['native/semantics/X87_SCALE.cpp.inc','native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h','native/semantics/x87_numeric_scope_fixture.cpp','native/semantics/x87_scale_fixture.cpp','native/semantics/x87_scale_numeric_fixture.cpp','native/semantics/x87_scale_probe.cpp','tools/x87_scale_experiment.py','tools/x87_scale_numeric_probe.py','tools/x87_scale_probe.py','tools/x87_scale_compare_probes.py']},retained_findings={'numeric-v1':'256 differences: an exactly zero scale operand preserves a denormal ST0 without generating a new UE. Nonzero subunit scales truncating to zero still enter exponent/underflow handling. Independent FXRSTOR and FLD80/FLDENV setup paths agree.','probe-v2-summary':'The inherited popped counter incorrectly equated nonzero TOP with a pop even though the two-load setup starts TOP=6. Raw results are intact; the independent comparison explicitly checks unchanged TOP=6/tags=192. Probe v3 fixes the metric to top_changed and reproduces every raw row.'},limitations=['Authored native code only; no game-derived object was linked, executed or newly accepted.','FSCALE ignores all PC encodings, truncates the raw scale toward zero, handles noncanonical/NaN/denormal priority explicitly and uses integer exponent/rounding operations. SoftFloat is used for scoped NaN propagation.','An unmasked exponent that remains outside the normal range after bias produces signed infinity or zero and precision, independent of the usual directed-rounding saturation choice. Exact-zero scale behavior is independently observed on this Intel host; AMD Jaguar equivalence remains unverified.','The 2809856 AOT/scope checks comprise 1761280 hardware comparisons and 1048576 four-thread load/store/arithmetic/scale scope checks. All 349046 pending faults match; no unsupported PC rejection applies to FSCALE.','Defined status, complete raw stack state, tags/TOP, unchanged memory/GPR flags, metadata, native fault PC/mask and host state isolation are checked. Undefined C0/C2/C3 are excluded.','Pointer/opcode profiles remain explicit. Hardware upper pointer bits remain outside the oracle; full native logical pointers are checked.','The present recovered x87 families now have bounded experimental checks, but exact selector coverage and module integration still need an audit. MMX is absent and compiler v7 rejects it.','Native runtime import/callback/exception/control closure and PS4 fault delivery remain open. No automatic promotion of existing v5/v9-sqrt startup objects.'],experimental_semantics='v31-scale',experimental_compiler='v7-mmx-guard',accepted_semantics='v9-sqrt',accepted_compiler='v5',compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-scale-evidence.json',report);summary=dict(status=report['status'],cases=scale['cases'],numeric_cases=report['numeric']['cases'],counts=counts,reproducible_artifacts=repeat);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
