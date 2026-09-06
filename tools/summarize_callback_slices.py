"""Audit branch-sensitive callback closure, the unknown entry finalizer and repeated AOT."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
old=root/'local/cfg/startup-recovery-v13-repeat';left=root/'local/cfg/startup-recovery-v14-slice';current=root/'local/cfg/startup-recovery-v15-repeat';a=root/'local/compiler-spike/callback-slice-compile-v1';b=root/'local/compiler-spike/callback-slice-compile-v2-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
 identities[name]=sha(current/name);assert identities[name]==sha(left/name)
summary=read(current/'summary.json');assert summary['counts']['recovery_entry']==21173 and summary['counts']['recovery_instruction']==873990 and summary['frontier_counts']['unresolved_callback_argument']==143
proof=read(root/'local/cfg/callback-slices-checked-v1/checked.json');assert proof['status']=='independent callback slices passed' and len(proof['records'])==2
complete=[r for r in proof['records'] if r['complete']];unknown=[r for r in proof['records'] if not r['complete']];assert len(complete)==1 and complete[0]['targets']==[dict(kind='module-rva',value=0x5f390)]
assert unknown[0]['entry']==0xa0 and unknown[0]['failures']==[dict(reason='entry-register',pc=0xa0,register='rsi')]
windows=read(root/'local/cfg/callback-slice-closure-checked-v1/checked.json');assert windows['unexplained']==0 and windows['windows']==10 and windows['shared_instructions']==577
old_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(old/'compilation-manifest.jsonl').open(encoding='utf-8'))}
new_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(current/'compilation-manifest.jsonl').open(encoding='utf-8'))};assert all(new_units[k]==v for k,v in old_units.items())
added=set(new_units)-set(old_units);assert len(added)==2
compiled=set();roots={};objects=[]
for directory in [root/'local/compiler-spike/startup-batch-all-v1',root/'local/compiler-spike/startup-fp-recompile-v2-repeat',root/'local/compiler-spike/callback-relocation-compile-v2-repeat']:
 for r in read(directory/'results.json'):
  if r['status']!='object_built':continue
  compiled.update((r['module'],pc) for pc in r['entries'])
  for pc in r['compiled_roots']:assert pc not in roots;roots[pc]=str(directory/r['folder'])
assert len(compiled)==21161
for x,y in zip(read(a/'results.json'),read(b/'results.json'),strict=True):
 assert x['status']==y['status']=='object_built' and x['input_sha256']==y['input_sha256'] and x['object_sha256']==y['object_sha256']==sha(b/y['folder']/'function.obj')
 folder=b/y['folder'];audit=read(folder/'audit.json');data=read(folder/'input.json');assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions']
 text=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(folder/'function.obj')],text=True);(out/'symbols.txt').write_text(text,encoding='utf-8');actual={int(m[1],16) for m in re.finditer(r'^sub_([0-9a-f]+)\s',text,re.M)};assert actual==set(audit['compiled_roots'])
 for pc in actual:assert pc not in roots;roots[pc]=str(folder)
 for unit in read(folder/'units.json'):assert unit['instruction_set_sha256']==new_units[y['module'],unit['entry']]
 compiled.update((y['module'],pc) for pc in y['entries']);objects.append(dict(folder=y['folder'],object_sha256=y['object_sha256'],object_bytes=y['object_bytes'],entries=y['entries'],roots=sorted(actual),missing_instruction_starts=y['missing_instruction_starts'],external_declarations=y['external_declarations']))
assert added<=compiled and len(compiled)==21163
for directory in [a,b]:
 identity=read(directory/'identity.json');assert identity['source_manifest_sha256']==identities['compilation-manifest.jsonl'] and identity['semantics_sha256']==sha(root/'build/extended-semantics-v9-sqrt/amd64_avx.bc')
runs={}
for suffix in ['callback-slice-checks-v1','callback-slices-v1','ghidra-callback-slices-v1','callback-slices-check-v1','callback-slice-integrated-checks-v1','callback-slice-integrated-checks-v2','startup-recovery-v14-slice','startup-recovery-v15-repeat','callback-slice-delta-v1','ghidra-callback-slice-closure-v1','callback-slice-closure-check-v1','callback-slice-compile-v1','callback-slice-compile-v2-repeat']:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'Ran 51 tests' in (root/'local/runs/20260906-p3-callback-slice-integrated-checks-v2/stderr.log').read_text()
report=dict(status='callback slice closure evidence pass; P3 remains open',current_directory=current.relative_to(root).as_posix(),summary=summary,reproducibility=identities,prior_instruction_sets_unchanged=21171,new_entries=2,new_instruction_addresses=2,proof=proof,independent_closure=windows,objects=objects,combined_compiled_entries=len(compiled),combined_objects=382,compiled_constructors=18444,remaining_compiler_rejections=2,remaining_quarantined_entries=8,remaining_unknown_callback_arguments=143,initial_relocation_candidates=142,entry_callback_binding=dict(entry=0xa0,site=0xbc,incoming_register='rsi',required_component='native process-entry finalizer callback binding and dispatch',status='unimplemented; no invented target',reference_source='external/shadPS4/src/core/linker.cpp',reference_sha256=sha(root/'external/shadPS4/src/core/linker.cpp'),reference_note='Pinned reference passes ProgramExitFunc in RSI. This corroborates the supplied instruction slice; it is not native port or PS4 execution evidence.'),focused_tests=51,runs=runs,gate='P3 remains open: 9,041 indirect-call records, 430 indirect-jump records, eight quarantined boundaries, 143 unknown callback arguments (142 have initial mutable candidates; one is the entry-provided finalizer), x87 state counterexamples and native import/callback/exception/control contracts. 21,163 entries compile; no native startup or playable port.',limitations=['Two destructor entry wrappers add two instructions; their destinations remain explicit native dispatch boundaries.','Backward slices retain cycles, partial/unsupported writes, volatile call results and missing/metadata-entry paths as unknown. Ghidra independently reconstructs register writes, constants and normal predecessors.','The first integration edit stopped at a text-match assertion before writing files; its named v1 test run covers the pre-integration 50-test suite. v2 covers 51 tests after integration.','Only authored semantic fixtures execute CPU code. These game-derived objects remain unlinked/unexecuted.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/callback-slice-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],compiled=len(compiled),objects=382,reproducibility=identities,new_object_bytes=sum(r['object_bytes'] for r in objects),unknown_callback_arguments=143));print(json.dumps(read(out/'summary.json')),flush=True)
