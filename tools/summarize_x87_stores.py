"""Audit numeric stores, exception priority and independently retained failures."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';sem=root/'build/extended-semantics-v29-store-priority';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in identity['authored_header_sha256'].items():assert sha(root/path)==digest
observations={}
for name,count,bad in [('x87-store-bindings-v1',5316668,0),('x87-store-bindings-v2-rounding-edges',6612668,1120),('x87-store-bindings-v3-tininess',6612668,288),('x87-store-bindings-v4-priority',6612668,0),('x87-store-bindings-v5-finite',6858428,0),('x87-store-bindings-v6-repeat',6858428,0),('x87-load-bindings-v8-stores',1876028,0)]:
 p=base/name;s=read(p/'summary.json');rows=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert s['groups']==rows and s['cases']==count and s['differing_cases']==bad and s['raw_sha256']==sha(p/'execute.stdout')
 if name not in ['x87-store-bindings-v1','x87-store-bindings-v2-rounding-edges','x87-store-bindings-v3-tininess']:assert s['semantics_sha256']==identity['semantics_sha256']
 observations[name]=s
stores=observations['x87-store-bindings-v6-repeat'];groups=stores['groups'];assert groups[0]==dict(form='numeric-scope',cases=524288,differing_cases=0)
assert sum(g.get('hardware_faults',0) for g in groups)==1030916 and sum(g.get('native_faults',0) for g in groups)==1030946 and sum(g.get('unsupported_cases',0) for g in groups)==30
assert all(not any(g['differences'].values()) and g['pointer_observation_differences']==g['opcode_observation_differences']==0 for g in groups[1:])
repeat={}
for name in ['function.bc','function.obj','numeric.obj','execute.stdout']:
 a=base/'x87-store-bindings-v5-finite'/name;b=base/'x87-store-bindings-v6-repeat'/name;assert a.read_bytes()==b.read_bytes();repeat[name]=sha(a)
independent={}
for name,count in [('x87-store-probe-v1',64512),('x87-store-probe-v2-edges',78848)]:
 p=base/name;s=read(p/'summary.json');rows=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()];assert s['cases']==len(rows)==count and s['raw_sha256']==sha(p/'execute.stdout')
 for r in rows:
  unmasked=r['status']&~r['control']&63
  if unmasked in [1,8,16]:assert not r['stored'] and r['top']==0
  elif unmasked==32:assert r['stored'] and r['top']==(r['form']>=2)
  else:assert unmasked==0
  if unmasked in [8,16]:assert not(r['status']&32)
  if r['form']>=4:assert not(r['status']&512)
 independent[name]=s
assert 'redefinition of' in (root/'build/extended-semantics-v28-store-priority/compile.stderr').read_text(encoding='utf-8')
runs={}
for suffix in ['x87-store-probe-v1','extended-semantics-v27-stores','x87-store-bindings-v1','x87-store-bindings-v2-rounding-edges','x87-store-bindings-v3-tininess','extended-semantics-v28-store-priority','extended-semantics-v29-store-priority','x87-store-probe-v2-edges','x87-store-bindings-v4-priority','x87-store-bindings-v5-finite','x87-store-bindings-v6-repeat','x87-load-bindings-v8-stores']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix in ['x87-store-bindings-v2-rounding-edges','x87-store-bindings-v3-tininess','extended-semantics-v28-store-priority'] else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert stores['library_sha256']==sha(root/'build/softfloat-v2-repeat/softfloat.lib')
ir=(base/'x87-store-bindings-v6-repeat/function.ll').read_text(encoding='utf-8');assert '__remill_fpu_' not in ir and all('@'+name in ir for name in ['__bb_x87_to_f32','__bb_x87_to_f64','__bb_x87_to_i16_trunc','__bb_x87_to_i32_trunc','__bb_x87_to_i64_trunc','__bb_native_x87_check_span','__bb_native_x87_record_instruction'])
report=dict(status='experimental x87 numeric stores and exception completion pass; P3 remains open',stores=stores,observations=observations,independent_hardware=independent,reproducible_artifacts=repeat,runs=runs,source_sha256={path:sha(root/path) for path in ['native/semantics/X87_STORE.cpp.inc','native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h','native/semantics/x87_numeric_scope_fixture.cpp','native/semantics/x87_store_fixture.cpp','native/semantics/x87_store_probe.cpp','tools/x87_store_experiment.py','tools/x87_store_probe.py']},retained_failures={'store-v2':'1120 differences at the normal/subnormal rounding boundary. The original unrounded source-exponent test incorrectly suppressed some stores that round into the normal range.','store-v3':'Using the rounded destination for the extra exact-tiny fact reduced differences to 288. Unmasked underflow signaled by the library also needed to suppress precision flags before write/pop decisions.','semantics-v28':'The build command accidentally listed SQRT twice and omitted the x87 extension tail; duplicate definitions rejected compilation. The fresh v29 command is complete. No output was overwritten or executed from the failed build.'},limitations=['Authored native AOT only, with seven store selectors: FST/FSTP m32/m64 and FISTTP m16/m32/m64. No game code was executed or newly accepted.','Five scoped native store conversions return destination bits, IEEE flags, magnitude-rounding direction and an extra rounded-tiny fact. Unsupported encodings are classified explicitly, pseudodenormals are normalized, and integer overflow returns the indefinite value with invalid rather than retaining a precision flag.','The instruction handles stack underflow first, then invalid/overflow/underflow priority. Unmasked IE/OE/UE suppress write/pop and unmasked OE/UE suppress newly generated PE. Unmasked PE still completes the store and optional pop.','Exact subnormal destinations can raise unmasked UE even when the numeric library reports no inexactness. Library UE plus the extra nonzero-source/rounded-subnormal-or-zero fact drive the instruction decision; an unrounded exponent threshold alone was disproved.','C1 is checked against magnitude rounding for floating stores and zero for truncating integer stores. Other undefined C0/C2/C3 remain excluded.','6334140 authored instruction cases plus 524288 concurrent scope checks make 6858428 checks. The matrix includes stack/tag/TOP patterns, masks/stickies, both explicit pointer/opcode profiles, random encodings, dense rounding boundaries, targeted finite random inputs, waiting suffixes and a two-store sequence.','1030916 matched hardware faults, 30 extra native pending-before-unsupported cases and 30 separate unsupported mappings do not implement PS4 fault delivery or general guest mappings.','Independent 64512/78848 hardware observations use FXRSTOR input and no Remill, SoftFloat, AOT or SEH comparison path. Intel-only observation does not settle AMD Jaguar equivalence.','Native helper and lifted function objects, bitcode and results reproduce byte-for-byte. No timing/performance conclusion is drawn.','Arithmetic, FSCALE, MMX coherence and native import/callback/exception/control closure remain open. Accepted startup artifacts remain v5 / v9-sqrt.'],experimental_semantics='v29-store-priority',experimental_compiler='v6-x87-opcode',accepted_semantics='v9-sqrt',accepted_compiler='v5',compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-stores-evidence.json',report);summary=dict(status=report['status'],cases=stores['cases'],hardware_faults=1030916,independent_hardware_cases=78848,reproducible_artifacts=repeat);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
