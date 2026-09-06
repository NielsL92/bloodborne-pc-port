"""Audit the reproducible native numeric-library candidate without promoting x87."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
source=read(root/'reports/softfloat-source.json');assert source['bytes']==729637 and source['sha256']=='21130ce885d35c1fe73fc1e1bf2244178167e05c6747cad5f450cc991714c746' and sha(Path(source['archive']))==source['sha256']
for name,digest in source['files'].items():assert sha(Path(source['source'])/name)==digest
builds={};objects=[]
for name in ['softfloat-v1','softfloat-v2-repeat']:
 p=root/'build'/name;s=read(p/'identity.json');assert s['objects']==302 and s['thread_local'] and s['specialization']=='8086' and s['library_sha256']==sha(p/'softfloat.lib')
 steps=read(p/'compile-steps.json');assert len(steps)==302 and all(r['exit_code']==0 for r in steps)
 for row in steps:assert sha(root/row['source'])==row['source_sha256'] and sha(p/(Path(row['source']).stem+'.obj'))==row['object_sha256']
 objects.append({r['source']:r['object_sha256'] for r in steps});builds[name]=s
assert objects[0]==objects[1] and builds['softfloat-v1']['library_sha256']==builds['softfloat-v2-repeat']['library_sha256']
probes={}
for name in ['softfloat-probe-v1','softfloat-probe-v2-repeat']:
 p=root/'local/compiler-spike'/name;s=read(p/'summary.json');rows=[json.loads(line) for line in (p/'execute.stdout').read_text(encoding='utf-8').splitlines()]
 assert s['groups']==rows and s['cases']==743392 and s['differing_cases']==0 and sum(r['cases'] for r in rows[:9])==481248 and rows[9]['cases']==262144
 assert s['raw_sha256']==sha(p/'execute.stdout') and s['library_sha256']==builds['softfloat-v1']['library_sha256'] and s['source_sha256']==sha(root/'native/semantics/softfloat_probe.cpp')
 assert all(r['differing_cases']==0 for r in rows);probes[name]=s
assert probes['softfloat-probe-v1']['raw_sha256']==probes['softfloat-probe-v2-repeat']['raw_sha256']
runs={}
for suffix in ['softfloat-source-v1','softfloat-build-v1','softfloat-probe-v1','softfloat-build-v2-repeat','softfloat-probe-v2-repeat']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']=='pass'
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
report=dict(status='bounded native numeric-library candidate passed; no x87 instruction integration or startup promotion',archive_sha256=source['sha256'],source_files=len(source['files']),license_sha256=source['license_sha256'],builds=builds,probes=probes,runs=runs,source_sha256={p:sha(root/p) for p in ['tools/fetch_softfloat.py','tools/build_softfloat.py','tools/softfloat_probe.py','native/semantics/softfloat_probe.cpp']},primary_sources=['https://www.jhauser.us/arithmetic/SoftFloat.html','https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html','https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat-source.html'],limitations=['481248 result/IEEE-flag hardware comparisons use authored masked x87 operations and canonical ext80 inputs. 262144 concurrent cases independently check per-thread rounding/precision/flag storage. These are not game execution or complete-library conformance coverage.','The candidate is ordinary C numerical code compiled ahead of time. It does not decode instructions, fetch guest code, interpret a CPU or provide fallback execution.','x87 denormal-operand flags, C1 rounding, stack/empty/overflow behavior, last pointers, memory boundaries and deferred faults must be handled outside these numerical operations.','SoftFloat does not guarantee noncanonical ext80 input behavior. Unsupported encodings, pseudodenormals and unmasked exponent-wrapped results need explicit x87 handling before use.','Thread-local library control variables still need a scoped save/set/restore wrapper for reentrant native integration. This probe sets them directly.','Only conversions from f32/f64/i64, conversions to f32/f64/truncated i64, and add/sub/mul are evaluated here. FSCALE is not supplied by the library.','All 302 native objects and the archive reproduce byte-for-byte. The fixed release hash was locally calculated from the HTTPS archive, not checked against an independently published publisher checksum.'],experimental_semantics='v19-mxcsr remains unchanged',accepted_semantics='v9-sqrt remains unchanged',compiled_entries=21168,remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/softfloat-evidence.json',report);summary=dict(status=report['status'],numeric_cases=481248,thread_cases=262144,objects=302,library_sha256=builds['softfloat-v1']['library_sha256']);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
