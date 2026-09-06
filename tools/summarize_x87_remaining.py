"""Audit remaining exact x87 sites and the fail-closed MMX compiler boundary."""
import hashlib,json,sys,zipfile
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);base=root/'local/compiler-spike'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
a=base/'x87-remaining-inventory-v1';b=base/'x87-remaining-inventory-v2-alias';old=read(a/'summary.json');current=read(b/'summary.json');sites=read(b/'remaining-arithmetic.json');assert current['x87_sites']==355 and current['remaining_sites']==len(sites)==9 and current['mmx_sites']==0 and old['remaining_sites']==20
assert [{k:v for k,v in row.items() if k!='owners'} for row in read(a/'x87-sites.json')]==[{k:v for k,v in row.items() if k!='owners'} for row in read(b/'x87-sites.json')]
assert old['database_sha256']==current['database_sha256'] and old['manifest_sha256']==current['manifest_sha256']
assert current['remaining_mnemonics']=={'fsubp':2,'fsubrp':2,'faddp':1,'fsub':1,'fmul':2,'fscale':1} and len(current['remaining_owners'])==5
checks={name:read(base/name/'summary.json') for name in ['sparse-mmx-checks-v1','sparse-checks-v7-mmx-guard','x87-opcode-checks-v2-mmx-guard']}
assert checks['sparse-mmx-checks-v1']['rejected_mmx']==12 and checks['sparse-mmx-checks-v1']['accepted_controls']==3 and checks['x87-opcode-checks-v2-mmx-guard']['cases']==112
assert len(checks['sparse-checks-v7-mmx-guard']['input_cases'])==10
runs={}
for suffix in ['x87-remaining-inventory-v1','x87-remaining-inventory-v2-alias','sparse-lift-v7-mmx-guard','sparse-mmx-checks-v1','sparse-checks-v7-mmx-guard','x87-opcode-checks-v2-mmx-guard','x87-remaining-evidence-audit-v1']:
 name='20260906-p3-'+suffix;p=root/'local/runs'/name;m=read(p/'manifest.json');assert m['status']==('failed' if suffix=='x87-remaining-evidence-audit-v1' else 'pass')
 with zipfile.ZipFile(p/'sources.zip') as z:
  for path,digest in m['source_sha256'].items():assert hashlib.sha256(z.read(path.replace(chr(92),'/'))).hexdigest()==digest
 runs[name]=dict(status=m['status'],source_commit=m['project_commit'],sources_sha256=sha(p/'sources.zip'),elapsed_seconds=m['elapsed_seconds'])
report=dict(status='nine arithmetic/scale sites remain in the current graph; new MMX rejects explicitly',inventory=current,remaining_sites=sites,checks=checks,runs=runs,source_sha256={p:sha(root/p) for p in ['native/sparse_lift/main.cpp','tools/x87_remaining_inventory.py','tools/sparse_mmx_checks.py']},retained_audit_failure='Audit v1 compared whole annotated x87 JSON files; selected ownership fields differ after alias classification. Audit v2 compares every instruction field excluding the intentionally selected owners annotation, and separately checks exact database/manifest hashes.',alias_correction='Capstone names DF E8..EF FUCOMPI; all 11 exact sites belong to the already characterized FUCOMIP selector. The first inventory omitted this spelling and overcounted remaining sites by 11. Static input bytes and database are unchanged.',limitations=['No MMX exists in the current recovered startup instruction graph. This says nothing about unknown indirect/callback targets or later gameplay.','Compiler v7 rejects decoded MM0..MM7 operands and EMMS/FEMMS before semantic lifting; shared MMX/x87 state remains unimplemented and cannot silently enter future native manifests.','The nine arithmetic/FSCALE instructions belong to five supplied libc entries. Family-level classification does not establish complete selector semantics, native control closure or execution coverage.','Accepted startup compiler/semantics remain v5 / v9-sqrt and 21168 compiled entries. Experimental compiler v7 / semantics v29 are not promoted.'],experimental_compiler='v7-mmx-guard',experimental_semantics='v29-store-priority',remaining_compiler_rejections=2,remaining_quarantined_entries=8,native_game_boot=False,native_port_playable=False)
write_json(root/'reports/x87-remaining-evidence.json',report);summary=dict(status=report['status'],remaining_sites=9,mmx_sites=0,rejected_mmx_authored_checks=12);write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
