"""Tie reproduced x87 counterexamples to exact recovered sites without claiming reachability."""
import collections,hashlib,json,sqlite3,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
source=root/'local/cfg/startup-recovery-v9-repeat';probe=root/'local/compiler-spike/x87-state-probe-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
summary=read(probe/'summary.json');assert summary['cases']==11520 and summary['differing_cases']==10176 and summary['raw_sha256']==sha(probe/'execute.stdout')
rows=[json.loads(x) for x in (probe/'execute.stdout').read_text().splitlines()];assert len(rows)==11520
counts=collections.Counter();specs=read(probe/'specs.json')
for r in rows:
 for key in r['differences']:counts[specs[r['form']]['name']+':'+key]+=1
assert dict(counts)==summary['differences']
c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
sites=[dict(r) for r in c.execute("select * from recovery_instruction where mnemonic like 'f%' or mnemonic in ('wait','emms') order by module,rva")]
for r in sites:r['owners']=[x[0] for x in c.execute('select entry from recovery_owner where module=? and rva=? order by entry',(r['module'],r['rva']))]
assert not any(r['mnemonic']=='fninit' for r in sites)
runs={}
for name,status in [('20260906-p3-x87-state-probe-v1','failed'),('20260906-p3-x87-state-probe-v2','pass')]:
 directory=root/'local/runs'/name;m=read(directory/'manifest.json');assert m['status']==status
 with zipfile.ZipFile(directory/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=status,source_commit=m['project_commit'],sources_sha256=sha(directory/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
for name in ('X87.cpp',):assert sha(root/'external/remill/lib/Arch/X86/Semantics'/name)==read(root/'build/extended-semantics-v9-sqrt/identity.json')['original_source_sha256']['external/remill/lib/Arch/X86/Semantics/'+name]
write_json(out/'sites.json',sites)
report=dict(status='x87 semantic gaps reproduced; serialization and execution remain blocked',probe=probe.relative_to(root).as_posix(),inventory=out.as_posix(),database_sha256=sha(source/'analysis.sqlite'),manifest_sha256=sha(source/'compilation-manifest.jsonl'),site_count=len(sites),owner_entries=len({(r['module'],entry) for r in sites for entry in r['owners']}),mnemonics=dict(collections.Counter(r['mnemonic'] for r in sites)),authored_probe=summary,runs=runs,original_remill_sources_unchanged=True,independent_sources=['https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf'],next_work=['Choose one canonical x87 register/tag/status/control representation before environment serialization.','Preserve guest x87 rounding and precision without leaking host controls; verify arithmetic under that contract.','Correct stack occupancy, overflow/underflow, split status synchronization, wait/exception transfer and full tag reconstruction/import behavior.','Do not add FXSAVE/FNSTENV/FLDENV merely to make two objects compile. Continue independent indirect/callback closure work while these precise semantic blockers remain.'],limitations=['11,520 authored bounded cases; 10,176 have at least one discrepancy. This is a counterexample corpus, not an estimate of game failure frequency.','Only selected fields and nonempty 80-bit payloads are compared, with all exceptions masked. Undefined condition flags, reserved bytes, hardware pointers and complete State are excluded.','Host-FP-control changes include the authored linked rounding helper; State control and serialized memory mismatches arise directly in pinned semantics.','FNINIT is absent from recovered startup instructions; its source regression is not an observed startup path.','The site inventory is static ownership, not execution coverage or an assertion that every instruction is incorrect.','No game bytes executed, no native startup, no runtime state fix, and no new compilation coverage.'])
write_json(root/'reports/x87-state-evidence.json',report);write_json(out/'summary.json',report)
print(json.dumps(dict(status=report['status'],sites=len(sites),owners=report['owner_entries'],mnemonics=report['mnemonics'])),flush=True)
