"""Verify COMI correction evidence and exact whole-object replacement ownership."""
import collections,hashlib,json,re,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike';source=root/'local/cfg/startup-recovery-v31-conditional-repeat';plan=base/'comi-replacement-plan-v1';new=base/'comi-replacement-compile-v2-repeat';old=base/'comi-replacement-compile-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
ps=read(plan/'summary.json');assert ps['sites']==49 and ps['affected_objects']==14 and ps['affected_entries']==753
for name,digest in ps['artifact_sha256'].items():assert sha(plan/name)==digest
assert sha(source/'compilation-manifest.jsonl')==ps['source_manifest_sha256'];assert sha(Path(ps['active_manifest']))==ps['active_manifest_sha256']
legacy=read(base/'comi-characterize-v1/summary.json');assert legacy['result']['cases']==851968 and legacy['result']['mismatched_cases']==245718 and legacy['result']['hardware_faults']==121600
checks=read(base/'comi-checks-v3-repeat/summary.json');assert checks['result']['cases']==851968 and checks['result']['hardware_faults']==121600
for key in ['mismatched_cases','remill_error_calls','fault_differences','flag_differences','mxcsr_differences','host_mxcsr_changes','full_state_differences','memory_exit_differences']:assert checks['result'][key]==0
for name in ['input.json','audit.json','function.bc','function.obj','execute.stdout']:
 assert sha(base/'comi-checks-v2-integer'/name)==sha(base/'comi-checks-v3-repeat'/name)
ir=(base/'comi-checks-v3-repeat/function.ll').read_text(encoding='utf-8');assert not re.search(r'\b(fcmp|fadd|fsub|fmul|fdiv)\b',ir) and '__remill_error' not in ir
sem=root/'build/extended-semantics-v34-comi-inline';identity=read(sem/'identity.json');assert sha(sem/'amd64_avx.bc')==checks['semantics_sha256']==identity['semantics_sha256']
for path,digest in identity['extension_sha256'].items():assert sha(Path(path))==digest
for path,digest in read(root/'build/extended-semantics-v31-scale/identity.json')['extension_sha256'].items():assert identity['extension_sha256'][path]==digest
current={}
for line in (source/'compilation-manifest.jsonl').open(encoding='utf-8'):
 u=json.loads(line);current[u['module_sha256'],u['entry']]=dict(hash=u['instruction_set_sha256'],ctor=u['constructor_ordinal'],issues=u['issues'])
active=read(Path(ps['active_manifest']));selected=read(plan/'selected-objects.json');newresults=read(new/'results.json');oldresults=read(old/'results.json');assert len(newresults)==len(oldresults)==len(selected)==14
for sel,before,after in zip(selected,oldresults,newresults,strict=True):
 assert before['folder']==after['folder'] and before['entries']==after['entries']==sel['entries'];assert after['compiled_roots']==sel['compiled_roots'];assert before['object_sha256']==after['object_sha256']
 for name in ['input.json','roots.json','units.json','audit.json','function.bc','function.obj']:assert sha(old/before['folder']/name)==sha(new/after['folder']/name)
 assert after['missing_instruction_starts']==after['original_missing_instruction_starts'];folder=new/after['folder'];audit=read(folder/'audit.json');mapping={m['module']:m['logical_base'] for m in read(new/'identity.json')['module_mapping']};bindings={s['address']:s for s in audit['decoded_selectors']}
 for site in sel['sites']:
  b=bindings[mapping[site['module']]+site['rva']];assert b['lifted'] and ('BB_COMISS' if site['mnemonic']=='vucomiss' else 'BB_COMISD') in b['implementation']
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
for suffix in ['comi-characterize-v1','extended-semantics-v34-comi-inline','comi-checks-v2-integer','comi-checks-v3-repeat','comi-replacement-plan-v1','comi-replacement-compile-v1','comi-replacement-compile-v2-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for file,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(file.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
evidence=dict(status='COMI/UCOMI correction passes authored tests; exact replacement manifest verified',legacy_counterexamples=legacy,checks=checks,replacement_plan=ps,replacement_compile=read(new/'summary.json'),active_manifest=str((out/'active-objects.json').relative_to(root)),active_manifest_sha256=sha(out/'active-objects.json'),compiled_objects=386,compiled_entries=21181,compiled_roots=21282,compiled_constructors=18444,runs=runs,retained_failures=['extended-semantics-v32-comi used a script path without the tools module import context; no output module was produced.','extended-semantics-v33-comi-module rejected ALWAYS_INLINE placement; v34 places the attribute before static.'],limitations=['All 49 recovered comparison instructions are VUCOMI forms; all 16 ordered/unordered scalar register/memory legacy/VEX forms were checked independently.','Only authored instructions were executed. No game object was linked or executed and PS4 exception delivery remains unimplemented.','The 14 previous objects remain preserved but are excluded from this new manifest. Every other object retains its original compiler/semantics identity.','New comparisons explicitly update guest MXCSR and preserve flags on unmasked faults; they do not use host floating arithmetic.','IR exit and COFF linkage inventories must be regenerated for this replacement set.'],p3_gate_passed=False,native_game_boot=False,native_port_playable=False)
write_json(out/'evidence.json',evidence);write_json(out/'summary.json',{k:evidence[k] for k in ['status','active_manifest','active_manifest_sha256','compiled_objects','compiled_entries','compiled_roots','compiled_constructors']});print(json.dumps(read(out/'summary.json')),flush=True)
