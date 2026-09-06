"""Audit repeated callback recovery and added AOT objects without claiming execution."""
import collections,hashlib,json,re,sqlite3,subprocess,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
old=root/'local/cfg/startup-recovery-v9-repeat';left=root/'local/cfg/startup-recovery-v12-relocations';current=root/'local/cfg/startup-recovery-v13-repeat';delta=root/'local/cfg/callback-candidate-delta-v1'
compile_left=root/'local/compiler-spike/callback-relocation-compile-v1';compile_right=root/'local/compiler-spike/callback-relocation-compile-v2-repeat'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
 identities[name]=sha(current/name);assert identities[name]==sha(left/name),name
assert read(current/'constructor-order.json')==read(root/'local/cfg/startup-v1/roots.json')
summary=read(current/'summary.json');assert summary['counts']['recovery_entry']==21171 and summary['counts']['recovery_instruction']==873988 and summary['counts']['recovery_issue']==8
assert summary['frontier_counts']['unresolved_callback_argument']==144 and summary['frontier_counts']['callback_relocation_target_candidate']==142
old_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(old/'compilation-manifest.jsonl').open(encoding='utf-8'))}
new_units={(u['module_sha256'],u['entry']):u['instruction_set_sha256'] for u in map(json.loads,(current/'compilation-manifest.jsonl').open(encoding='utf-8'))}
assert all(new_units[k]==v for k,v in old_units.items())
added=set(new_units)-set(old_units);assert added=={(r['module'],r['start']) for r in read(delta/'new-entries.json')} and len(added)==11
checked=read(root/'local/cfg/callback-candidates-checked-v1/checked.json');assert checked['source_db_sha256']==identities['analysis.sqlite'] and checked['unexplained']==0 and checked['shared_instructions']==4030
# The new export bindings are exact NID/library/provider matches, still mutable.
from tools.formats import ElfImage
con=sqlite3.connect((current/'analysis.sqlite').as_uri()+'?mode=ro',uri=True)
module_paths=dict(con.execute('select hash,path from module'));links={};exports=collections.defaultdict(list)
for h,p in module_paths.items():
 assert sha(p)==h;links[h]=ElfImage(Path(p).read_bytes()).linkage()
 for symbol in links[h]['symbols']:
  if symbol['defined'] and symbol['type']==2:exports[tuple(symbol[k] for k in ('nid','library','module'))].append((h,symbol['value']))
bindings=[]
for row in read(delta/'records.json'):
 if row['kind']!='callback_relocation_binding_unvalidated':continue
 h=row['module'];d=row['detail'];relocation=next(r for r in links[h]['relocations'] if r['offset']==d['slot']);assert relocation==d['relocation'] and relocation['type']==6 and relocation['addend']==0
 symbol=links[h]['symbols'][relocation['symbol']];assert symbol==d['symbol'] and symbol['type']==2
 targets=exports[tuple(symbol[k] for k in ('nid','library','module'))];assert len(targets)==1 and d['candidates']==[dict(module=targets[0][0],target=targets[0][1])]
 assert con.execute("select count(*) from recovery_edge where module=? and entry=? and source=? and kind='unresolved_callback_argument'",(h,row['entry'],row['source'])).fetchone()[0]==1
 bindings.append((h,d['slot'],symbol['nid'],targets[0][0],targets[0][1]))
assert len(bindings)==142 and len(set(bindings))==2
roots={};compiled=set();prior_objects=0
for directory in [root/'local/compiler-spike/startup-batch-all-v1',root/'local/compiler-spike/startup-fp-recompile-v2-repeat']:
 for r in read(directory/'results.json'):
  if r['status']!='object_built':continue
  prior_objects+=1
  for pc in r['compiled_roots']:assert pc not in roots;roots[pc]=str(directory/r['folder'])
  compiled.update((r['module'],pc) for pc in r['entries'])
assert len(compiled)==21150 and prior_objects==380
objects=[]
for x,y in zip(read(compile_left/'results.json'),read(compile_right/'results.json'),strict=True):
 assert x['status']==y['status']=='object_built' and x['entries']==y['entries'] and x['input_sha256']==y['input_sha256']
 folder=compile_right/y['folder'];assert x['object_sha256']==y['object_sha256']==sha(folder/'function.obj')
 audit=read(folder/'audit.json');data=read(folder/'input.json');assert set(audit['decoded_addresses'])=={r['address'] for r in data['instructions']} and not audit['unvisited_manifest_instructions']
 actual_text=subprocess.check_output([str(LLVM/'bin/llvm-nm.exe'),'--defined-only','--format=posix',str(folder/'function.obj')],text=True);(out/(y['folder']+'-symbols.txt')).write_text(actual_text,encoding='utf-8')
 actual={int(m.group(1),16) for m in re.finditer(r'^sub_([0-9a-f]+)\s',actual_text,re.M)};assert actual==set(audit['compiled_roots'])
 for pc in actual:assert pc not in roots,(pc,roots.get(pc));roots[pc]=str(folder)
 for unit in read(folder/'units.json'):assert unit['instruction_set_sha256']==new_units[y['module'],unit['entry']]
 compiled.update((y['module'],pc) for pc in y['entries']);objects.append(dict(folder=y['folder'],entries=y['entries'],object_sha256=y['object_sha256'],object_bytes=y['object_bytes'],roots=len(actual),missing_path_records=len(y['missing_instruction_starts']),external_declarations=y['external_declarations']))
assert added<=compiled and len(compiled)==21161
for directory in [compile_left,compile_right]:
 identity=read(directory/'identity.json');assert identity['source_manifest_sha256']==identities['compilation-manifest.jsonl'] and identity['semantics_sha256']==sha(root/'build/extended-semantics-v9-sqrt/amd64_avx.bc')
runs={}
names=['sysv-candidate-checks-v1','startup-recovery-v11-sysv','startup-sysv-delta-v1','callback-relocation-checks-v1','callback-relocation-checks-v2','startup-recovery-v12-relocations','startup-recovery-v13-repeat','callback-candidate-delta-v1','ghidra-callback-candidates-v1','callback-candidates-check-v1','callback-relocation-compile-v1','callback-relocation-compile-v2-repeat']
for suffix in names:
 name='20260906-p3-'+suffix;directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
assert 'Ran 42 tests' in (root/'local/runs/20260906-p3-callback-relocation-checks-v2/stderr.log').read_text()
report=dict(status='callback relocation closure evidence pass; P3 remains open',current_directory=current.relative_to(root).as_posix(),summary=summary,reproducibility=identities,prior_instruction_sets_unchanged=len(old_units),new_entries=len(added),new_instruction_addresses=407,conditional_constant_callback_records=11,initial_relocated_callback_records=142,initial_bindings=[dict(source_module=h,slot=slot,nid=nid,target_module=other,target=target) for h,slot,nid,other,target in sorted(set(bindings))],unknown_callback_records=144,unknown_callback_records_without_initial_candidate=2,independent_check=checked,objects=objects,combined_compiled_entries=len(compiled),compiled_constructors=18444,combined_objects=prior_objects+len(objects),duplicate_logical_roots=0,remaining_compiler_rejections=2,remaining_quarantined_entries=8,focused_tests=42,runs=runs,gate='P3 remains open: 9,041 indirect-call records, 430 indirect-jump records, eight quarantined boundaries, 144 unknown callback arguments (142 with initial mutable binding candidates), x87 semantic failures, and native import/callback/exception/control contracts. All 18,444 initial constructor entries compile; no native startup or playable port.',limitations=['Preserved normal SysV return registers are explicit conditional ABI assumptions; asynchronous/nonlocal control is unvalidated.','A mutable slot initial binding never removes its unknown runtime callback argument. Exactly two supplied libc function exports seed eleven transitive bodies.','Old instruction sets are unchanged; new object symbols have no overlap with retained successful batches. Objects were not linked or executed.','Original source/modules and runs remain unchanged. The x87 counterexample report still blocks native state serialization.'],native_game_boot=False,native_port_playable=False)
write_json(root/'reports/callback-relocation-evidence.json',report);write_json(out/'summary.json',dict(status=report['status'],entries=21171,compiled=len(compiled),objects=report['combined_objects'],new_object_bytes=sum(o['object_bytes'] for o in objects),reproducibility=identities,ghidra_shared=4030))
print(json.dumps(read(out/'summary.json')),flush=True)
