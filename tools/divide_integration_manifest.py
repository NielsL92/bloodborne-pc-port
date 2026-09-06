"""Verify DIV/IDIV correction evidence and exact whole-object replacement ownership."""
import collections,hashlib,json,re,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike';source=root/'local/cfg/startup-recovery-v31-conditional-repeat';plan=base/'divide-replacement-plan-v1';new=base/'divide-replacement-compile-v2-repeat';old=base/'divide-replacement-compile-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
ps=read(plan/'summary.json');assert ps['sites']==28 and ps['affected_objects']==13 and ps['affected_entries']==632
for name,digest in ps['artifact_sha256'].items():assert sha(plan/name)==digest
assert sha(source/'compilation-manifest.jsonl')==ps['source_manifest_sha256'];assert sha(Path(ps['active_manifest']))==ps['active_manifest_sha256']
legacy=read(base/'divide-characterize-v3-sites/summary.json');assert legacy['result']['cases']==327680 and legacy['result']['mismatched_cases']==218424 and legacy['result']['hardware_faults']==218424
checks=read(base/'divide-checks-v5-repeat/summary.json');assert checks['result']['cases']==327680 and checks['result']['hardware_faults']==218424
for key in ['mismatched_cases','remill_error_calls','aot_host_exceptions','fault_decision_differences','fault_pc_differences','result_differences','host_mxcsr_changes','full_state_differences','memory_exit_differences','explicit_fault_contract_differences']:assert checks['result'][key]==0
for name in ['input.json','audit.json','function.bc','function.obj','execute.stdout']:
 assert sha(base/'divide-checks-v4-unsigned'/name)==sha(base/'divide-checks-v5-repeat'/name)
for cohort in ['divide-characterize-v3-sites','divide-checks-v4-unsigned','divide-checks-v5-repeat']:
 folder=base/cohort;summary=read(folder/'summary.json');assert sha(folder/'oracle.json')==summary['oracle_sha256'];oracle=read(folder/'oracle.json');assert sum(oracle['cases_per_form'])==327680
 for name,digest in oracle['case_sha256'].items():assert sha(folder/name)==digest==sha(base/'divide-checks-v5-repeat'/name)
host_cases=[json.loads(line) for line in (base/'divide-characterize-v3-sites/execute.stdout').read_text(encoding='utf-8').splitlines() if 'host_exception_case' in line];assert len(host_cases)==2 and {r['form'] for r in host_cases}=={24,27} and all(r['trial']==159 and r['code']==0xc0000095 for r in host_cases)
ir=(base/'divide-checks-v5-repeat/function.ll').read_text(encoding='utf-8');assert not re.search(r'\b(fcmp|fadd|fsub|fmul|fdiv)\b',ir) and '__remill_error' not in ir
sem=root/'build/extended-semantics-v35-divide';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==checks['semantics_sha256']==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in read(root/'build/extended-semantics-v34-comi-inline/identity.json')['extension_sha256'].items():assert identity['extension_sha256'][path]==digest
regression=read(base/'comi-checks-v4-divide-regression/summary.json');assert regression['result']['cases']==851968 and regression['result']['mismatched_cases']==0 and regression['semantics_sha256']==checks['semantics_sha256']
for name in ['function.bc','function.obj','execute.stdout']:assert sha(base/'comi-checks-v4-divide-regression'/name)==sha(base/'comi-checks-v3-repeat'/name)
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(hash=u['instruction_set_sha256'],ctor=u['constructor_ordinal'],issues=u['issues'])
active=read(Path(ps['active_manifest']));selected=read(plan/'selected-objects.json');newresults=read(new/'results.json');oldresults=read(old/'results.json');assert len(newresults)==len(oldresults)==len(selected)==13
for sel,before,after in zip(selected,oldresults,newresults,strict=True):
 assert before['folder']==after['folder'] and before['entries']==after['entries']==sel['entries'];assert after['compiled_roots']==sel['compiled_roots'];assert before['object_sha256']==after['object_sha256']
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:assert sha(old/before['folder']/name)==sha(new/after['folder']/name)
 assert after['missing_instruction_starts']==after['original_missing_instruction_starts'];folder=new/after['folder'];audit=read(folder/'audit.json');mapping={m['module']:m['logical_base'] for m in read(new/'identity.json')['module_mapping']};bindings={s['address']:s for s in audit['decoded_selectors']}
 for site in sel['sites']:
  b=bindings[mapping[site['module']]+site['rva']];assert b['lifted'] and site['expected_implementation'] in b['implementation']
 active[sel['index']]=dict(source_batch=new.name,**{k:after[k] for k in ['folder','module','entries','compiled_roots','object_sha256','object_bytes']})
entries=collections.Counter();roots=collections.Counter()
for obj in active:
 folder=base/obj['source_batch']/obj['folder'];assert sha(folder/'function.obj')==obj['object_sha256']
 for u in read(folder/'units.json'):
  key=(obj['module'],u['entry']);assert u['instruction_set_sha256']==current[key]['hash'];entries[key]+=1
 roots.update(obj['compiled_roots'])
assert len(active)==386 and len(entries)==21181 and len(roots)==21282 and set(entries.values())=={1} and set(roots.values())=={1};assert set(entries)==set(current) and not any(u['issues'] for u in current.values());assert sum(current[k]['ctor'] is not None for k in entries)==18444
write_json(out/'active-objects.json',active)
runs={}
for suffix in ['divide-characterize-v3-sites','extended-semantics-v35-divide','divide-checks-v4-unsigned','divide-checks-v5-repeat','divide-replacement-plan-v1','divide-replacement-compile-v1','divide-replacement-compile-v2-repeat','comi-checks-v4-divide-regression']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for file,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(file.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
evidence=dict(status='DIV/IDIV correction passes authored tests; exact replacement manifest verified',legacy_counterexamples=legacy,host_exception_cases=host_cases,checks=checks,comparison_regression=regression,replacement_plan=ps,replacement_compile=read(new/'summary.json'),active_manifest=str((out/'active-objects.json').relative_to(root)),active_manifest_sha256=sha(out/'active-objects.json'),compiled_objects=386,compiled_entries=21181,compiled_roots=21282,compiled_constructors=18444,runs=runs,retained_failures=['divide-characterize-v1 terminated with host integer overflow before completing. V2 records arithmetic exceptions in a process-local authored-test handler; v3 additionally records both exact failing inputs. All outputs remain preserved.'],limitations=['All 28 recovered division instructions are 32/64-bit forms. Tests cover signed/unsigned 8/16/32/64-bit forms, memory and aliases of quotient/remainder registers.','Python integer arithmetic supplies the independent oracle, separately checked on hardware. Success arithmetic flags are undefined and excluded; fault flags/state/PC are checked.','Only authored instructions were executed; the exception-capture bridge is not a production guest unwind or PS4 exception delivery implementation.','The thirteen previous objects remain preserved but are excluded from this manifest. Every other object retains its original compiler/semantics identity.','IR exit and COFF linkage inventories must be regenerated for this replacement set.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(out/'evidence.json',evidence);write_json(out/'summary.json',{k:evidence[k] for k in ['status','active_manifest','active_manifest_sha256','compiled_objects','compiled_entries','compiled_roots','compiled_constructors']});print(json.dumps(read(out/'summary.json')),flush=True)
