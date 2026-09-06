"""Audit authored numeric/register arithmetic evidence without promoting startup."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';sem=root/'build/extended-semantics-v30-arithmetic';identity=read(sem/'identity.json')
assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in identity['authored_header_sha256'].items():assert sha(root/path)==digest
observations={}
for name,count,bad in [('x87-arithmetic-numeric-v1',491520,576),('x87-arithmetic-numeric-v2-recenter',491520,0),('x87-arithmetic-numeric-v3-expanded',5529600,0),('x87-arithmetic-numeric-v4-edges',8271360,0),('x87-arithmetic-bindings-v1',7528448,0),('x87-arithmetic-bindings-v2-scope',7790592,0),('x87-arithmetic-bindings-v3-repeat',7790592,0),('x87-store-bindings-v7-arithmetic',7120572,0),('x87-load-bindings-v9-arithmetic',2138172,0)]:
 p=base/name;s=read(p/'summary.json');rows=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()]
 assert s['groups']==rows and s['cases']==count and s['differing_cases']==bad and s['raw_sha256']==sha(p/'execute.stdout')
 if 'bindings' in name:assert s['semantics_sha256']==identity['semantics_sha256']
 assert s['library_sha256']==sha(root/'build/softfloat-v2-repeat/softfloat.lib');observations[name]=s
arithmetic=observations['x87-arithmetic-bindings-v3-repeat'];groups=arithmetic['groups'];assert groups[0]==dict(form='numeric-scope',cases=786432,differing_cases=0)
assert len(groups)==58 and all(not any(g['differences'].values()) and not g['pointer_observation_differences'] and not g['opcode_observation_differences'] for g in groups[1:])
counts={key:sum(g.get(key,0) for g in groups) for key in ['hardware_faults','native_faults','unsupported_cases']};assert counts==dict(hardware_faults=845672,native_faults=1429352,unsupported_cases=817152)
repeat={}
for name in ['function.bc','function.obj','numeric.obj','execute.stdout']:
 a=base/'x87-arithmetic-bindings-v2-scope'/name;b=base/'x87-arithmetic-bindings-v3-repeat'/name;assert a.read_bytes()==b.read_bytes();repeat[name]=sha(a)
p=base/'x87-arithmetic-probe-v1';independent=read(p/'summary.json');assert independent['raw_sha256']==sha(p/'execute.stdout');rows=0;reserved={};normal={}
for line in (p/'execute.stdout').open(encoding='utf-8'):
 r=json.loads(line);rows+=1;unmasked=r['status']&~r['control']&63
 if unmasked&3:assert r['top']==0 and not(r['status']&512)
 else:assert r['top']==int(r['form']<3)
 assert unmasked in [0,1,2,8,16,32,40,48]
 pc=(r['control']>>8)&3
 if pc in [1,3]:
  key=(r['form'],r['type'],r['pair'],r['signs'],r['control']&~0x300,r['input_c1']);value=tuple(r[k] for k in ['status','top','tags','sig0','exp0','sig1','exp1']);(reserved if pc==1 else normal)[key]=value
assert rows==independent['cases']==491520 and len(reserved)==122880 and reserved==normal
runs={};suffixes=['x87-arithmetic-probe-v1','x87-arithmetic-numeric-v1','x87-arithmetic-numeric-v2-recenter','x87-arithmetic-numeric-v3-expanded','x87-arithmetic-numeric-v4-edges','x87-arithmetic-semantics-v30','x87-arithmetic-bindings-v1','x87-arithmetic-bindings-v2-scope','x87-arithmetic-bindings-v3-repeat','x87-store-bindings-v7-arithmetic','x87-load-bindings-v9-arithmetic']
for suffix in suffixes:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix=='x87-arithmetic-numeric-v1' else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
  if suffix=='x87-arithmetic-bindings-v3-repeat':
   for path in ['native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h','native/semantics/x87_numeric_scope_fixture.cpp','native/semantics/X87_ARITHMETIC.cpp.inc','native/semantics/x87_arithmetic_fixture.cpp']:assert z.read(path)==(root/path).read_bytes()
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
ir=(base/'x87-arithmetic-bindings-v3-repeat/function.ll').read_text(encoding='utf-8');assert '__remill_fpu_' not in ir and 'x86_fp80' not in ir
for name in ['__bb_x87_add','__bb_x87_sub','__bb_x87_mul','__bb_native_x87_unsupported','__bb_native_x87_fault','__bb_native_x87_record_instruction']:assert '@'+name in ir
sites=read(base/'x87-remaining-inventory-v2-alias/remaining-arithmetic.json');checked=[r for r in sites if r['mnemonic']!='fscale'];remaining=[r for r in sites if r['mnemonic']=='fscale'];assert len(checked)==8 and len(remaining)==1 and remaining[0]['rva']==0x413f2
report=dict(status='experimental x87 register arithmetic checks pass; FSCALE and P3 remain open',arithmetic=arithmetic,numeric=observations['x87-arithmetic-numeric-v4-edges'],observations=observations,independent_hardware=independent,host_reserved_precision_pairs=len(reserved),counts=counts,reproducible_artifacts=repeat,runs=runs,checked_site_families=checked,remaining_fscale=remaining,source_sha256={path:sha(root/path) for path in ['native/semantics/X87_ARITHMETIC.cpp.inc','native/semantics/x87_numeric.cpp','native/semantics/x87_numeric.h','native/semantics/x87_numeric_scope_fixture.cpp','native/semantics/x87_arithmetic_fixture.cpp','native/semantics/x87_arithmetic_numeric_fixture.cpp','native/semantics/x87_arithmetic_probe.cpp','tools/x87_arithmetic_experiment.py','tools/x87_arithmetic_numeric_probe.py','tools/x87_arithmetic_probe.py']},retained_failure='Numeric v1 had 576 differences: directly scaling both add/sub operands by -24576 made a much smaller operand unrepresentable. The replacement recenters the computation before rounding, keeps a distant nonzero tail, then restores the wrapped result exponent. Both the failed run and its sources are preserved.',limitations=['Authored Windows AOT only. No game-derived object was linked, executed or newly accepted.','Five register selectors cover FSUBP/FSUBRP/FADDP/FSUB/FMUL; all eight register indices, waiting suffixes and two mixed sequences are checked. Undefined C0/C2/C3 are excluded.','Valid precision controls 0/2/3 use 24/53/64 significant bits and all four rounding modes. The numeric matrix has 8117760 hardware comparisons and 153600 reserved-control rejections.','Reserved PC=1 is deliberately unsupported, although 122880 independent host pairs matched PC=3. No host observation implicitly selects a guest policy.','The AOT matrix has 5603328 hardware comparisons, 583680 pending-before-reserved checks and 817152 explicit reserved-control rejections, plus 786432 concurrent native load/store/arithmetic scope checks. These are not all hardware execution comparisons.','Unmasked invalid/denormal suppress result/pop. Unmasked arithmetic overflow/underflow/precision complete result and optional pop; wrapped arithmetic may also raise precision. Memory store suppression rules are different.','Native numeric calls restore all four SoftFloat TLS controls. The library source and previous accepted startup objects remain unchanged. There is no guest instruction fetch/decode, interpreter, JIT or original-game CPU fallback.','Both pointer/opcode profiles remain explicit. Hardware pointer comparison is limited to the low 32 bits; native logical pointers and metadata are fully checked.','Intel-host observations do not establish AMD Jaguar equivalence. Native pending/unsupported fixture services do not implement general Windows unwind or PS4 fault delivery.','FSCALE at libc 0x413f2 in entry 0x413e0 remains uncharacterized. MMX is absent from the present graph and rejected by compiler v7 if encountered. Native startup/import/callback/exception/control closure remains open.'],experimental_semantics='v30-arithmetic',experimental_compiler='v7-mmx-guard',accepted_semantics='v9-sqrt',accepted_compiler='v5',compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-arithmetic-evidence.json',report);summary=dict(status=report['status'],cases=arithmetic['cases'],numeric_cases=report['numeric']['cases'],counts=counts,reproducible_artifacts=repeat);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
