"""Audit authored x87 exception evidence without promoting experimental startup semantics."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sem=root/'build/extended-semantics-v15-x87-flags';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in identity['original_source_sha256'].items():assert sha(root/path)==digest
accepted=root/'build/extended-semantics-v9-sqrt';assert sha(accepted/'amd64_avx.bc')==read(accepted/'identity.json')['semantics_sha256']
probes={}
for name,cases in [('x87-stack-probe-v3',1499136),('x87-fault-probe-v7-memory',720896)]:
 directory=root/'local/compiler-spike'/name;s=read(directory/'summary.json');groups=[json.loads(line) for line in (directory/'execute.stdout').read_text().splitlines()]
 assert s['groups']==groups and s['cases']==cases==sum(g['cases'] for g in groups) and s['differing_cases']==0
 assert all(g['differing_cases']==0 and not any(g['differences'].values()) for g in groups)
 assert sha(directory/'execute.stdout')==s['raw_sha256'] and sha(directory/'fixture.exe')==s['fixture_sha256'] and s['semantics_sha256']==identity['semantics_sha256']
 assert all(step['exit_code']==0 for step in read(directory/'steps.json'))
 probes[name]=dict(summary=s,summary_sha256=sha(directory/'summary.json'),input_sha256=sha(directory/'input.json'),object_sha256=sha(directory/'function.obj'),audit_sha256=sha(directory/'audit.json'))
fault_groups=probes['x87-fault-probe-v7-memory']['summary']['groups'];delivered=sum(g['hardware_faults'] for g in fault_groups);assert delivered==285424==sum(g['native_faults'] for g in fault_groups)
independent=root/'local/compiler-spike/x87-compare-probe-v1';summary=read(independent/'summary.json');rows=[json.loads(line) for line in (independent/'execute.stdout').read_text().splitlines()];invalid=[r for r in rows if r['status']&1 and not r['control']&1]
assert len(rows)==summary['cases']==65536 and len(invalid)==summary['unmasked_invalid_cases']==24960
assert sum((r['after']&0x45)==0x45 for r in invalid)==summary['unmasked_invalid_unordered_flags']==24960
assert sum((r['before']&0x45)!=(r['after']&0x45) for r in invalid)==summary['unmasked_invalid_flags_changed']==21840
assert sha(independent/'execute.stdout')==summary['raw_sha256'] and sha(independent/'fixture.exe')==summary['fixture_sha256']
retained={}
for name,expected in [('x87-fault-probe-v1',77952),('x87-fault-probe-v2',11616),('x87-fault-probe-v3',11616),('x87-fault-probe-v4',744),('x87-fault-probe-v5',14064)]:
 directory=root/'local/compiler-spike'/name;s=read(directory/'summary.json');assert s['differing_cases']==expected and sha(directory/'execute.stdout')==s['raw_sha256'];retained[name]=dict(cases=s['cases'],differing_cases=expected,summary_sha256=sha(directory/'summary.json'))
runs={}
suffixes=['x87-stack-probe-v2','x87-fault-probe-v1','x87-fault-probe-v2','x87-fault-probe-v3','extended-semantics-v13-x87-faults','x87-fault-probe-v4','extended-semantics-v14-x87-compare','x87-fault-probe-v5','x87-compare-probe-v1','extended-semantics-v15-x87-flags','x87-fault-probe-v6','x87-stack-probe-v3','x87-fault-probe-v7-memory']
for suffix in suffixes:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
report=dict(status='authored x87 stack/control fault evidence passed; experimental module remains unaccepted for startup',experimental_semantics=sem.relative_to(root).as_posix(),semantics_sha256=identity['semantics_sha256'],accepted_semantics=accepted.relative_to(root).as_posix(),accepted_semantics_sha256=sha(accepted/'amd64_avx.bc'),selector_replacements=identity['selector_replacements'],probes=probes,delivered_faults=delivered,independent_comparison_probe=summary,retained_counterexamples=retained,runs=runs,source_sha256={p:sha(root/p) for p in ['native/semantics/X87_STATE.cpp.inc','native/semantics/x87_fault_probe.cpp','native/semantics/x87_compare_probe.cpp','tools/x87_fault_probe.py','tools/x87_compare_probe.py']},manual_dispute=dict(instruction_reference='https://cdrdv2-public.intel.com/812383/253666-sdm-vol-2a.pdf',older_correction='https://www.citi.umich.edu/projects/citi-netscape/pdf/24333721.pdf',correction_section='Intel Pentium II specification update A16, printed page 61',note='Search-indexed primary Intel correction says comparison result flags are set even with unmasked invalid. The instruction reference says the opposite. Two independent authored Intel-host probes agree with the correction. Direct retrieval of the older PDF returned 502; preserve this source limitation. AMD Jaguar behavior remains unverified.'),gate='No new startup objects, no native link or game execution. 21,168 entries compile; two x87 serializers and eight disputed manifests remain. P3 stays open.',limitations=['The sixteen experimental selectors do not repair memory conversion or arithmetic families; do not combine this partial stack model with original x87 semantics for startup acceptance.','Hardware SEH and the authored native System V nonlocal callback frame validate bounded fault behavior, not Windows guest unwind or PS4 exception delivery.','Guest last instruction/data pointers, FOP, undefined condition flags, empty payloads and reserved fields remain excluded.','AMD primary indexed instruction text is available but direct PDF retrieval returned 404. Intel host agreement is not AMD Jaguar execution proof.','Every input control/status/tag and nonempty payload is checked against its immediate hardware import in the fault fixture. v1 used inconsistent summary bits and is retained as diagnostic evidence, not a semantic failure count.','v2 had a fixture PC-offset error for ABI-specific memory encodings; v3 maps explicit instruction labels and leaves the actual semantic discrepancies visible.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-fault-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],masked_cases=1499136,fault_cases=720896,delivered_faults=delivered,semantics_sha256=identity['semantics_sha256']));print(json.dumps(read(out/'summary.json')),flush=True)
