"""Publish the audited continuation pointers while retaining prior checkpoint history."""
import datetime as dt,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();report_path=root/'reports/startup-services-evidence.json';r=json.loads(report_path.read_text(encoding='utf-8'));assert r['compiled_entries']==21173 and r['compiled_objects']==382
stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
source=r['source'];active=r['active_objects_manifest'];digest=r['active_objects_sha256'];repro=r['reproducible_artifacts']
block=f"""## Current continuation — {stamp}

Execution continues autonomously; user action: none. Read `reports/startup-services.md` / `reports/startup-services-evidence.json`. Three exact service-call annotations reduce fence quarantines from eight to five. The complete static census is **21,173 entries / 382 objects, zero compiler rejections**, including all 18,444 initial constructors with unique entry and logical-root ownership. Native termination, cleanup, exceptions and callback dispatch remain unimplemented obligations. No game-derived object was linked or executed.

Canonical recovery is now `{source}`: 21,178 entries / 874,265 instruction addresses across eight modules. Its database, compilation manifest, frontier and constructor order reproduce v23-services byte-for-byte. Database SHA256 `{repro['recovery/analysis.sqlite']}`; manifest SHA256 `{repro['recovery/compilation-manifest.jsonl']}`. It retains 9,044 unknown indirect-call records, 430 indirect jumps and 143 unknown callback arguments, plus three explicit unresolved native service-control records.

Use `{active}` as the complete current object manifest, SHA256 `{digest}`. It retains all 380 previously accepted objects and adds the two repeated startup-services-compile-v3-repeat objects (three entries / 34 instructions / 4,255 bytes). Retained objects keep their recorded compiler/semantic identities. New work continues with build/sparse-lift-v8-selector-audit, build/extended-semantics-v31-scale and build/softfloat-v2-repeat/softfloat.lib. Do not re-add the five removed pre-x87 objects or the 12 diagnostic x87 objects.

Next: libc throw/rethrow entries 0x60510, 0x60560 and 0x606f0 still depend on helper 0x60750 with unresolved virtual calls at 0x60811 and 0x6081f. Preliminary supplied relocation/symbol inspection identifies the first initial target as libc 0x48f00 (`__class_type_info::cast_to`, 10 bytes), which is not yet recovered or Ghidra-checked. Independently verify its two symbol-based relocation steps and body before adding a conditional target; preserve mutable object/table and symbol-binding uncertainty. Main entries 0x210b0e0 and 0x210b940 remain quarantined through helper 0x210ad70's unknown virtual call at 0x210ad84 followed by exit, or longjmp with an unknown restored context.

P3 remains open; no native game boot or playable port exists. P1 route/profiling/audio work is unchanged. The memory-pressured v24 repeat was stopped during integrity checking with outputs preserved; v25 releases obsolete recovery maps and uses a 64 MiB SQLite cache before the same full integrity check, which passed. Continue using tools/run_record.py and fresh output directories. No restart, read approval, paid component or user action is needed.

"""
for name in ['HANDOFF.md','reports/STATUS.md']:
 p=root/name;s=p.read_text(encoding='utf-8');start=s.index('## Current continuation');end=s.index('Updated 2026-09-06 02:12 UTC.',start);s=s[:start]+block+s[end:]
 if name.endswith('STATUS.md'):
  lines=s.splitlines()
  for i,line in enumerate(lines):
   if line.startswith('| P3 |'):lines[i]='| P3 | Startup compiler and runtime gates remain open | 21,178 manifest entries; 29 independently checked helper summaries and three exact service-site annotations; 21,173 entries / 382 static objects including all 18,444 initial constructors. Zero compiler rejections; five quarantines and native service/control closure remain. |'
   if line.startswith('| P4-P9 |'):lines[i]='| P4-P9 | Not started; required runtime/game gates remain | 9,044 unknown indirect-call records, 430 indirect jumps, five fallthrough findings, 143 unknown callback arguments and native import/callback/exception/service contracts remain open. |'
  s='\n'.join(lines)+'\n'
 p.write_text(s,encoding='utf-8')
short=f"""Updated {stamp}: three independently checked, exact service-call annotations reduce fence quarantines to five. The current complete static census is 21,173 entries / 382 objects; zero compiler rejections and all 18,444 initial constructors are represented. Continue with `{source}` and `{active}`. See `reports/startup-services.md` and `reports/startup-services-evidence.json` for the conditional contracts, reproducible objects, retained failures and exact remaining work. P3 remains open; native service/control execution is not established. Earlier dated checkpoints below are historical.

"""
for name in ['reports/control-flow.md','reports/compiler-spike.md','reports/startup-closure.md']:
 p=root/name;s=p.read_text(encoding='utf-8');first,rest=s.split('\n',1);p.write_text(first+'\n\n'+short+rest.lstrip('\n'),encoding='utf-8')
p=root/'reports/control-flow-evidence.json';d=json.loads(p.read_text(encoding='utf-8'));d['startup_service_control']=dict(path='reports/startup-services-evidence.json',sha256=sha(report_path),result=r);write_json(p,d)
text=f"""# Exact startup service-control boundaries

Updated {stamp}. P3 remains open. No native game boot or playable port exists.

The static census is now **21,173 entries / 382 objects**, with zero compiler rejections, five quarantined manifests and all 18,444 initial constructors represented exactly once. The active manifest is `{active}` (SHA256 `{digest}`). It adds two repeated objects totaling 4,255 bytes and 34 instructions to the prior 380-object set. Original packages, hardlinked views and previous runs are unchanged.

## What the three annotations establish

| Supplied entry and final service call | Exact binding and condition | Obligations retained |
| --- | --- | --- |
| libc 0x1f560; call 0x1f56b to PLT 0xe0 | Debug-exception NID OMDRKKAZ8I4, libkernel/libkernel, only within the supplied abort wrapper with RDI=0xa002000b and RSI=0 | Native abort/debug binding, signal/exception disposition and nonlocal handler effects; unexpected service return |
| libc 0x5ff10; call 0x5ff5d to PLT 0x5a0 | _exit NID 6Z83sYWFlA8, libkernel/libkernel | Process status, all-thread termination and resource teardown; earlier libc exit callbacks remain unresolved |
| main 0x207f990; call 0x207f99b to PLT 0x2bc0d38 | scePthreadExit NID 3kg7rT0NQIs, libkernel/libkernel | Exit value/join, LIFO cancellation cleanup, thread-data destructors, last-thread process termination and native callback dispatch |

These are conditional no-ordinary-return annotations at exact module/entry/call-site identities. They do not implement services. The public [abort contract](https://pubs.opengroup.org/onlinepubs/9699919799/functions/abort.html), [_exit contract](https://pubs.opengroup.org/onlinepubs/9799919799/functions/_exit.html) and [pthread_exit contract](https://pubs.opengroup.org/onlinepubs/009696899/functions/pthread_exit.html) supply independent API obligations. Pinned shadPS4 symbols and reference implementations corroborate identity, without being console observations or a native implementation. The generic debug service can reject a nonzero second argument and return; no global noreturn rule was added.

The new objects retain three explicit missing paths after the service calls. A future native runtime must diagnose an unexpected return, not execute the trailing NOP or adjacent bytes. The original import frontier is unchanged, and three unresolved_native_service_control records retain all service effects. The former abort NOP is the only removed instruction; only the three intended manifests change. Every existing unknown-target count is unchanged.

## Independent checks and repetition

Ghidra checks all eight original quarantines plus both key helpers and the signal-import caller: 11 windows, 753 shared instruction identities, zero byte/boundary disagreements and zero recovery-only instructions. One extra instruction follows an existing annotated stack-protector-failure call and is explained from Ghidra's own flow. Raw independent outputs are preserved. Ghidra separately confirms the abort argument operands and the only straight-line entry path to the service call. Fifty-four focused tests pass, including modified arguments/bytes, wrong providers, new landing-pad roots, other call sites, and the unchanged generic debug-call return path.

`{source}` reproduces v23's database, manifest, frontier and constructor order byte-for-byte. Database SHA256 `{repro['recovery/analysis.sqlite']}`; manifest SHA256 `{repro['recovery/compilation-manifest.jsonl']}`. The complete recovery contains 21,178 entries / 874,265 instruction addresses across eight modules. The two successful compile runs reproduce input, roots, units, audit, bitcode and object files exactly. The evidence audit verifies every active entry against the current instruction-set hash, one owner for each entry and compiled logical root, and all issue-free manifests and initial constructors.

Report publication v1 read existing Markdown using the Windows default code page and failed on a UTF-8 character. Its partial outputs were preserved separately and restored from the verified pre-change source commit before an explicit UTF-8 retry. The source snapshot and failure log remain.\n\nCompile v1 started before its selection artifact existed and failed before lifting or compilation. V2 waits for the completed delta; V3 repeats it. Recovery v24 finished decoding/export but encountered severe memory pressure during the full SQLite integrity check: about 937 MiB free of 31.8 GiB physical memory, with 545,586 process read operations recorded. It was stopped after 1,006 seconds; its database, exports, source snapshot and logs remain. A read-only cache warm-up did not promptly finish that check. V25 releases no-longer-needed recovery maps and uses a connection-local 64 MiB SQLite cache, then performs the same full integrity check. It passed in 106 seconds overall and reproduced v23 artifacts. This operational observation is not a controlled performance comparison or a gameplay performance claim.

## Remaining concrete work

Five quarantines remain: libc 0x60510, 0x60560 and 0x606f0 lead through 0x60750's unresolved virtual calls; main 0x210b0e0 and 0x210b940 lead through 0x210ad70's virtual callback/exit branch or longjmp. No unknown callback was assumed to return or terminate. Preliminary inspection identifies libc 0x60811's initial table target as 0x48f00 through a data-symbol relocation at 0xbe2d0 and a function-symbol relocation at 0xba9e0. Its 10-byte body and relocation chain require independent checks and recovery; they are not part of this accepted census. Object/table mutation, symbol binding and the subsequent what() target remain unresolved.

The replacement x87 object's unnamed libkernel NID VADc3MNQ3cM resolves in pinned reference sources to `signal`. At libc 0x13027 the supplied code tail-calls it with numeric arguments 9 and 0. This changes signal disposition; it does not raise a signal or supply a non-null callback. The exact console result, errno and native binding remain open. POSIX permits an error when setting the default disposition for an uncatchable signal; no unconditional success or nonreturn behavior was invented. [Signal contract](https://pubs.opengroup.org/onlinepubs/9799919799/functions/signal.html).

For reproduction, preserve every run and use `tools/run_record.py --id UNIQUE -- COMMAND`. Run `tools.startup_service_inventory`, `tools.ghidra_recovery_check --exception-roots`, `tools.check_startup_services`, the focused tests and `tools.check_ghidra_window_closure` first. Regenerate recovery from the default original startup-db-v1 seed with the existing jump/control/callback/object evidence and the additional `--service-site-evidence local/cfg/startup-services-checked-v1/contracts.json`. `tools.startup_service_delta` verifies the exact change and creates the three-entry compile selection. Use `tools.startup_batch_compile` with v8 sparse lift / v31 semantics, then `tools.summarize_startup_services`. Exact argv and immutable source snapshots are in the recorded runs listed in the evidence JSON. Do not use an extended database as the seed.

P1 Hunter's Dream route, profiler overhead/cost separation and intermittent opening audio mutex crash remain independent and unchanged. No user action or paid component is needed.
"""
(root/'reports/startup-services.md').write_text(text,encoding='utf-8')
p=root/'reports/decisions/0002-promoted-state-and-control-boundaries.md';s=p.read_text(encoding='utf-8');s+=f"\nService-site continuation ({stamp}): three exact module/entry/call-site contracts now remove ordinary fallthrough conditionally while adding unresolved native service-control obligations. The abort rule additionally requires its independently checked constant arguments and entry path. Generic debug-service calls retain their return path. Five exception/nonlocal quarantines and all unknown callback/indirect targets remain. These annotations and 21,173 compiled entries are static evidence; the native runtime and P3 gate remain open. See reports/startup-services.md.\n";p.write_text(s,encoding='utf-8')
print(json.dumps(dict(status='continuation reports updated',timestamp=stamp,active_manifest=active)))
