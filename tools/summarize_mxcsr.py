"""Audit canonical guest MXCSR semantics and original host-state counterexamples."""
import hashlib,json,sqlite3,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
base=root/'local/compiler-spike';sem=root/'build/extended-semantics-v19-mxcsr';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for name,digest in identity['extension_sha256'].items():assert sha(Path(name))==digest
observations={}
for name in ['mxcsr-original-v1','mxcsr-native-v1']:
 p=base/name;s=read(p/'summary.json');raw=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()]
 assert s['groups']==raw and s['cases']==812640 and s['differing_cases']==sum(g['differing_cases'] for g in raw)
 assert s['raw_sha256']==sha(p/'execute.stdout') and s['fixture_sha256']==sha(p/'fixture.exe')
 observations[name]=s
original=observations['mxcsr-original-v1'];native=observations['mxcsr-native-v1'];assert original['differing_cases']==812592 and native['differing_cases']==0 and native['semantics_sha256']==identity['semantics_sha256']
assert all(not any(g['differences'].values()) for g in native['groups'])
assert sum(g['hardware_faults'] for g in native['groups'])==13056 and sum(g['native_faults'] for g in native['groups'])==111360 and sum(g['policy_cases'] for g in native['groups'])==98304 and sum(g['unsupported_cases'] for g in native['groups'])==96
ir=(base/'mxcsr-native-v1/function.ll').read_text(encoding='utf-8');old_ir=(base/'mxcsr-original-v1/function.ll').read_text(encoding='utf-8')
assert '__remill_fpu_' not in ir and '@__bb_native_mxcsr_mask' in ir and '@__bb_native_mxcsr_fault' in ir
assert '__remill_fpu_get_rounding' in old_ir and '__remill_fpu_set_rounding' in old_ir
suite=read(base/'mxcsr-floating-regression-v1/summary.json');assert suite['status']=='combined authored semantic suite pass' and suite['semantics_sha256']==identity['semantics_sha256']
for name,count in [('minmax',1572864),('round',4194304),('sqrt',3145728)]:assert suite['results'][name]['summary']['result']['status']=='pass' and suite['results'][name]['summary']['result']['aot_cases']==count
images=read(base/'x87-image-bindings-v3-mxcsr/summary.json');assert images['cases']==557864 and images['differing_cases']==0 and images['semantics_sha256']==identity['semantics_sha256'] and images['raw_sha256']==sha(base/'x87-image-bindings-v3-mxcsr/execute.stdout')
runs={}
for suffix in ['mxcsr-original-v1','extended-semantics-v19-mxcsr','mxcsr-native-v1','mxcsr-floating-regression-v1','x87-image-bindings-v3-mxcsr']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
source=root/'local/cfg/startup-recovery-v22-cache-repeat';db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
sites=[dict(r) for r in db.execute("SELECT module,rva,bytes,mnemonic,operands FROM recovery_instruction WHERE mnemonic IN ('ldmxcsr','stmxcsr','vldmxcsr','vstmxcsr') ORDER BY module,rva")];assert len(sites)==5
owners=list(db.execute('SELECT module,entry,rva FROM recovery_owner WHERE rva IN (0x2fd21,0x2fd39,0x3045a,0x30469,0x2fcf5)'))
for site in sites:site['owners']=[r['entry'] for r in owners if r['module']==site['module'] and r['rva']==site['rva']];assert len(site['owners'])==1
assert {r['entry'] for r in owners}=={0x2fcb0,0x2fd00,0x30430}
accepted=root/'build/extended-semantics-v9-sqrt';assert sha(accepted/'amd64_avx.bc')==read(accepted/'identity.json')['semantics_sha256']
report=dict(status='experimental canonical MXCSR semantics and authored fault contracts passed; P3 startup gate remains open',native=native,original_counterexamples=original,floating_regressions=suite,image_regression=images,runs=runs,recovered_sites=sites,source_sha256={p:sha(root/p) for p in ['native/semantics/MXCSR.cpp.inc','native/semantics/mxcsr_fixture.cpp','tools/mxcsr_experiment.py']},primary_sources=['https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/programmer-references/26568.pdf','https://docs.amd.com/api/khub/documents/sD1_QL~h4Afq2_tvzxqqSQ/content','https://cdrdv2-public.intel.com/868137/325462-089-sdm-vol-1-2abcd-3abcd-4.pdf'],primary_source_access='AMD instruction text and mask rules and Intel LDMXCSR operation retrieved from primary-source search results. Direct AMD instruction PDF URL returns 404.',limitations=['812592 original differences include required service/host-helper contract differences; per-category State/memory/host-state/fault counters are separate in the retained raw results. The original run was intentionally characterization, so wrapper pass did not mean semantic pass.','13056 reserved-bit faults are compared with Intel hardware. 98304 DAZ-reserved faults use an explicit 0xffbf profile rule, not hardware that lacks DAZ.','96 unavailable-memory cases are authored unsupported mapping diagnostics, not PS4 page-fault delivery. Guest memory services own access boundaries.','The profile service returns a normalized allowed-bit mask. A raw zero FXSAVE mask must be interpreted by the future runtime as 0xffbf; it is not automatically zero allowed bits. The existing image-profile service must use the same guest feature choice.','No native game object was executed or newly accepted. Experimental v19 remains unaccepted for startup pending coherent x87 memory/arithmetic, MMX alias and other runtime/control contracts.','The new selectors support the decoded normal forms. Feature-disabled or malformed instruction #UD, general guest exception delivery and asynchronous faults are not implemented by this fixture.'],compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/mxcsr-evidence.json',report);summary=dict(status=report['status'],cases=812640,original_differing_cases=812592,hardware_faults=13056,policy_faults=98304,unsupported_mapping_cases=96,recovered_sites=5,experimental_semantics_sha256=identity['semantics_sha256']);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
