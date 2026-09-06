"""Audit constructor compilation, packed/transfer contracts, repeatability and remaining rejects."""
import collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
base=root/'local/compiler-spike/startup-batch-all-v1';left_dir=root/'local/compiler-spike/startup-fp-recompile-v1';right_dir=root/'local/compiler-spike/startup-fp-recompile-v2-repeat'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
prior=read(base/'results.json');left=read(left_dir/'results.json');right=read(right_dir/'results.json')
old_units={(r['module'],pc) for r in prior if r['status']=='object_built' for pc in r['entries']}
rejected={(r['module'],pc) for r in prior if r['status']!='object_built' for pc in r['entries']}
assert {(r['module'],pc) for r in right for pc in r['entries']}==rejected and len(rejected)==48
roots={pc:r['folder'] for r in prior if r['status']=='object_built' for pc in r['compiled_roots']};new_units=set();objects=[];traps=set();failures=[]
decoded={r['address']:r for r in read(root/'local/compiler-spike/startup-rejection-inspection-v1/decoded.json')}
for x,y in zip(left,right,strict=True):
 assert (x['module'],x['entries'],x['status'],x['input_sha256'])==(y['module'],y['entries'],y['status'],y['input_sha256'])
 folder=right_dir/y['folder']
 if y['status']!='object_built':
  error=(folder/'lift.stderr').read_text();match=re.fullmatch(r'REJECT: unsupported Remill instruction semantics at (\d+)\s*',error);assert match
  pc=int(match[1]);failures.append(dict(module=y['module'],entry=y['entries'][0],logical_pc=pc,selector=decoded[pc]['selector'],bytes=decoded[pc]['bytes'],folder=y['folder']));continue
 assert x['object_sha256']==y['object_sha256']==sha(folder/'function.obj') and sha(left_dir/x['folder']/'audit.json')==sha(folder/'audit.json')
 audit=read(folder/'audit.json');data=read(folder/'input.json');assert set(audit['decoded_addresses'])=={i['address'] for i in data['instructions']}
 assert set(audit['explicit_native_trap_addresses'])=={r['address'] for r in data.get('native_traps',[])}
 assert audit['semantic_instruction_count']+len(audit['explicit_native_trap_addresses'])==len(data['instructions'])
 symbols=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(folder/'function.obj')],text=True)
 (out/(y['folder']+'-symbols.txt')).write_text(symbols,encoding='utf-8');actual={int(m.group(1),16) for m in re.finditer(r'^sub_([0-9a-f]+)\s',symbols,re.M)};assert actual==set(audit['compiled_roots'])
 for pc in actual:assert pc not in roots;roots[pc]=y['folder']
 traps.update(audit['explicit_native_trap_addresses']);new_units.update((y['module'],pc) for pc in y['entries'])
 objects.append(dict(folder=y['folder'],module=y['module'],entries=y['entries'],object_sha256=y['object_sha256'],object_bytes=y['object_bytes'],native_traps=audit['explicit_native_trap_addresses'],external_declarations=y['external_declarations']))
assert len(new_units)==46 and len(objects)==8 and len(traps)==16 and len(failures)==2 and not new_units&old_units
sem_dir=root/'build/extended-semantics-v9-sqrt';sem=read(sem_dir/'identity.json');sem_hash=sha(sem_dir/'amd64_avx.bc');assert sem_hash==sem['semantics_sha256']
for group in ('extension_sha256','original_source_sha256','linked_bitcode_sha256'):
 for path,digest in sem[group].items():assert sha(root/path)==digest
assert sha(root/'build/remill/lib/Arch/X86/Runtime/amd64_avx.bc')==sem['original_semantics_sha256']
for directory in (left_dir,right_dir):
 identity=read(directory/'identity.json');assert identity['semantics_sha256']==sem_hash and identity['source_manifest_sha256']==sha(root/'local/cfg/startup-recovery-v9-repeat/compilation-manifest.jsonl')
main='d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9';order=read(root/'local/cfg/startup-recovery-v9-repeat/constructor-order.json');assert len(order)==18444 and all((main,r['target']) in old_units|new_units for r in order)
suite=read(root/'local/compiler-spike/semantic-suite-v9/summary.json');assert suite['status']=='combined authored semantic suite pass' and suite['semantics_sha256']==sem_hash
checks={}
for family,count in dict(bmi=34816,shuffle=32768,blend=122880,rsqrt=399360,packed=262144,select=376832,transfer=593408,minmax=1572864,round=4194304,sqrt=3145728).items():
 check=suite['results'][family]['summary'];assert check['semantics_sha256']==sem_hash and check['result']['aot_cases']==count;checks[family]=check
runs={}
for name in ['20260905-p3-fp-characterization-v1', '20260905-p3-minmax-model-v1', '20260905-p3-build-extended-semantics-v7-minmax', '20260905-p3-minmax-semantics-v1', '20260905-p3-minmax-semantics-v2', '20260905-p3-minmax-semantics-v3-diagnostic', '20260906-p3-minmax-semantics-v4-diagnostic', '20260906-p3-minmax-semantics-v5', '20260906-p3-minmax-semantics-v6', '20260906-p3-minmax-wrapper-disassembly-v1', '20260906-p3-startup-minmax-recompile-v1', '20260906-p3-build-extended-semantics-v8-round', '20260906-p3-round-semantics-v1', '20260906-p3-sqrt-model-v1', '20260906-p3-build-extended-semantics-v9-sqrt', '20260906-p3-sqrt-semantics-v1', '20260906-p3-semantic-suite-v9', '20260906-p3-startup-fp-recompile-v1', '20260906-p3-startup-fp-recompile-v2-repeat']:
 p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if name in ['20260905-p3-minmax-semantics-v1', '20260905-p3-minmax-semantics-v2', '20260905-p3-minmax-semantics-v3-diagnostic', '20260906-p3-minmax-semantics-v4-diagnostic', '20260906-p3-minmax-semantics-v5', '20260906-p3-startup-minmax-recompile-v1', '20260906-p3-startup-fp-recompile-v1', '20260906-p3-startup-fp-recompile-v2-repeat'] else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],elapsed_seconds=m['elapsed_seconds'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'))
selector_text=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(sem_dir/'amd64_avx.bc')],text=True)
(out/'semantic-selectors.txt').write_text(selector_text,encoding='utf-8');selectors={m.group(1) for m in re.finditer(r'^ISEL_([^ ]+) ',selector_text,re.M)};assert len(selectors)>1000
missing=[]
for failure in failures:
 data=read(right_dir/failure['folder']/'input.json')
 for instruction in data['instructions']:
  info=decoded[instruction['address']]
  if info['selector'] not in selectors and not info['is_error_category']:missing.append(dict(module=failure['module'],entry=failure['entry'],logical_pc=instruction['address'],selector=info['selector'],bytes=info['bytes']))
report=dict(status='precise floating semantics and complete constructor compilation evidence pass; P3 open',directory=right_dir.relative_to(root).as_posix(),audit_directory=out.as_posix(),new_compiled_entries=len(new_units),combined_compiled_entries=len(old_units|new_units),compiled_constructors=len(order),constructor_targets=len(order),remaining_compiler_rejections=len(failures),remaining_quarantined_manifests=8,duplicate_logical_roots=0,byte_identical_repeat=True,objects=objects,remaining_first_failures=failures,remaining_all_missing_selector_sites=missing,remaining_all_missing_selectors=dict(collections.Counter(r['selector'] for r in missing)),remaining_first_selectors=dict(collections.Counter(r['selector'] for r in failures)),semantic_module_sha256=sem_hash,original_semantics_unchanged=True,checks=checks,runs=runs,model_checks={name:read(root/'local/compiler-spike'/name/'summary.json') for name in ('minmax-model-v1','sqrt-model-v1')},limitations=['Only authored instruction code executed; game-derived objects were not linked or executed.','All initially ordered constructor entries compile, but direct/indirect/callback/exception/runtime closure remains open. Mutable constructor targets are not resolved by this static initial table.','RSQRT uses an LLVM native x86 SSE intrinsic with host approximation output and the documented error bound. AMD Jaguar bit-exact estimates remain unverified.','Existing floating-point semantic support is not proof of complete MXCSR/exception behavior.','Explicit native SIMD faults preserve pre-instruction destination/stack/PC and update guest sticky flags; the fixture uses a bounded System V nonlocal escape. Native Windows unwind and PS4 exception delivery are unimplemented.', 'The CRT escape failed with STATUS_BAD_FUNCTION_TABLE. A Windows builtin escape had biased-frame-pointer restoration errors; the verified System V fixture frame restores host nonvolatile registers.', 'Remaining x87 environment/save selectors are not accepted: pinned FNINIT uses the overlapping FSAVE view while stack code uses FXSAVE; stack push/pop does not update tags. These require independent characterization and a coherent state contract.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/fp-semantics-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],compiled_constructors=len(order),combined_compiled_entries=len(old_units|new_units),byte_identical_repeat=True,remaining_first_selectors=report['remaining_first_selectors'],remaining_all_missing_selectors=report['remaining_all_missing_selectors']))
print(json.dumps(read(out/'summary.json')),flush=True)
