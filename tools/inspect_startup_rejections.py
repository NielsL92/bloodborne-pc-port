"""Inspect every instruction in rejected startup entries, retaining error categories."""
import argparse,collections,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('survey',type=Path);p.add_argument('inspector',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
results=[r for r in json.loads((a.survey/'results.json').read_text()) if r['status']!='object_built'];mapping=json.loads((a.survey/'identity.json').read_text())['module_mapping'];bases={r['module']:r['logical_base'] for r in mapping};rows={};owners=collections.defaultdict(list)
for r in results:
 data=json.loads((a.survey/r['folder']/'input.json').read_text())
 for ins in data['instructions']:
  pc=ins['address'];assert pc not in rows or rows[pc]==ins;rows[pc]=ins;owners[pc].append(dict(module=r['module'],entry=r['entries'][0],rva=pc-bases[r['module']]))
write_json(a.out/'input.json',[rows[pc] for pc in sorted(rows)]);exe=a.inspector.resolve()
with (a.out/'stdout.log').open('wb') as out,(a.out/'stderr.log').open('wb') as err:r=subprocess.run([str(exe),str(a.out/'input.json'),str(a.out/'decoded.json')],stdout=out,stderr=err,timeout=120)
assert r.returncode==0;decoded=json.loads((a.out/'decoded.json').read_text());assert len(decoded)==len(rows) and all(r['same_boundary'] for r in decoded)
problems=[dict(**r,owners=owners[r['address']]) for r in decoded if not r['selector_present'] or r['is_error_category'] or r['is_invalid_category'] or not r['decoded']]
write_json(a.out/'problems.json',problems)
selection={(o['module'],o['entry']) for r in problems for o in r['owners']};write_json(a.out/'selection.json',[dict(module=h,start=pc,reason='compiler semantic or decoder rejection') for h,pc in sorted(selection)])
summary=dict(status='read-only decoder/selector inspection complete',inspector_sha256=sha(exe),survey_identity_sha256=sha(a.survey/'identity.json'),rejected_entries=len(results),instructions=len(rows),problem_instructions=len(problems),missing_selectors=dict(collections.Counter(r['selector'] for r in problems if not r['selector_present'])),error_categories=dict(collections.Counter(r['selector'] for r in problems if r['is_error_category'])),invalid_categories=sum(r['is_invalid_category'] for r in problems),decode_failures=sum(not r['decoded'] for r in problems),independent_entries=len(selection),limitations='Missing selector presence and explicit error categories are distinct from instruction decode failure. Static inspection only; no semantic correctness or execution claim.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
