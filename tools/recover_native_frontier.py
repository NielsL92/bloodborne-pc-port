"""Recover an additive CFG dependency frontier from an actual native unknown target."""
import argparse,collections,json,sqlite3
from pathlib import Path
from tools.cfg_recover_startup import Recovery,sha,write_json
p=argparse.ArgumentParser();p.add_argument('probe',type=Path);p.add_argument('out',type=Path);p.add_argument('--max-entries',type=int,default=64);a=p.parse_args();assert 1<=a.max_entries<=256
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
source=Path('local/cfg/startup-recovery-v31-conditional-repeat');registry=Path('local/runtime/registry-v7-memory-repeat');probe=read(a.probe/'summary.json');assert probe['game_aot_execution'] and not probe['original_byte_cpu_execution'] and probe['fault']['reason']==27
pc=int(probe['fault']['pc'],16);calls=[json.loads(s) for s in (a.probe/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];assert calls[-1]['event']=='dispatch' and calls[-1]['target']==pc;assert sha(a.probe/'startup.exe')==probe['executable_sha256'] and sha(a.probe/'native-calls.jsonl')==probe['control_trace_sha256'];assert sha(registry/'identity.json')==probe['registry_identity']
modules=read(registry/'modules.json');module=next(m for m in modules if m['logical_base']<=pc<m['logical_base']+0x100000000);bases={m['module']:m['logical_base'] for m in modules};known=read(a.probe/'compilation-targets.json');assert pc not in {r['pc'] for r in known};base_db=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
prior=read('local/runs/20260906-p3-startup-recovery-v31-conditional-repeat/manifest.json');argv=prior['argv'];assert prior['status']=='pass';flags={argv[i]:Path(argv[i+1]) for i in range(4,len(argv)) if argv[i].endswith('-evidence')};options={k[2:].replace('-','_'):v for k,v in flags.items()};options.update(sysv_callee_saved_candidates=True,initial_callback_relocation_candidates=True)
class Delta(Recovery):
 def recover(self,h,start):
  end,reason=self.fence(h,start)
  previous=base_db.execute('select rva,size,bytes from recovery_instruction where module=? and rva<? and rva+size>?',(h,end,start)).fetchall()
  for at,size,raw in previous:
   assert self.images[h].at_va(at,size).hex()==raw
   for byte in range(at,at+size):self.byte_owners[h][byte]=at
  self.overlap_evidence.append(dict(module=h,entry=start,prior_instructions=previous))
  return super().recover(h,start)
r=Delta(Path('local/cfg/startup-db-v1'),Path('local/cfg/startup-v1/roots.json'),a.out,a.max_entries,20000,**options);r.overlap_evidence=[];r.queue.clear();r.requested={(h,start) for h,start in base_db.execute('select module,start from recovery_entry')};r.requested.update((row['module'],row['pc']-bases[row['module']]) for row in known);assert (module['module'],pc-module['logical_base']) not in r.requested
# The copied metadata and ordered constructors stay intact. Discard only automatic
# initial requests in this new delta DB, since this run starts at the observed fault.
r.db.execute('DELETE FROM recovery_request');r.request(module['module'],pc-module['logical_base'],'observed_native_unknown_target');r.identity.update(parent_recovery_db_sha256=sha(source/'analysis.sqlite'),parent_compilation_targets_sha256=sha(a.probe/'compilation-targets.json'),observed_probe_sha256=sha(a.probe/'summary.json'),observed_trace_sha256=sha(a.probe/'native-calls.jsonl'),observed_entry=pc,scope='Additive frontier only; parent recovery and every unresolved record remain unchanged. Previously compiled entries are external dependencies.');write_json(a.out/'identity.json',r.identity)
while r.queue and len(r.done)<a.max_entries:
 h,start=r.queue.popleft();r.recover(h,start);r.done.add((h,start));r.db.commit();print(json.dumps(dict(entries=len(r.done),queued=len(r.queue),entry=hex(bases[h]+start))),flush=True)
write_json(a.out/'prior-overlaps.json',r.overlap_evidence);pending=list(r.queue);r.export();summary=read(a.out/'summary.json');units=[json.loads(s) for s in (a.out/'compilation-manifest.jsonl').read_text(encoding='utf-8').splitlines()];c=sqlite3.connect((a.out/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);windows=[]
for u in units:
 pads=[v[0] for v in c.execute('select distinct landing_pad from exception_call_site where module=? and range_start=? and landing_pad is not null order by landing_pad',(u['module_sha256'],u['entry']))];windows.append(dict(module=u['module_sha256'],start=u['entry'],end=u['fence'],additional_roots=pads))
write_json(a.out/'windows.json',windows);result=dict(status='additive CFG recovered pending independent decoding and compilation',observed_entry=pc,entries=len(units),instructions=summary['counts']['recovery_instruction'],issues=summary['decode_issue_kinds'],frontier=summary['frontier_counts'],pending=pending,source_db_sha256=sha(source/'analysis.sqlite'),delta_db_sha256=summary['db_sha256'],manifest_sha256=summary['manifest_sha256'],windows_sha256=sha(a.out/'windows.json'),identity_sha256=sha(a.out/'identity.json'),original_byte_cpu_execution=False,native_game_boot=False,limitations=['This delta uses the established recovery annotations and metadata fences. Fences, initial pointers and successful decoding do not prove function boundaries or execution coverage.','Previously compiled roots remain external dependencies. The parent canonical database and all its unresolved records are preserved.','Indirect calls, callbacks, exception/nonlocal behavior, mutable tables and any budget/decode issues remain explicit; independent Ghidra and compilation checks are still required.']);write_json(a.out/'delta.json',result);print(json.dumps(result),flush=True)
