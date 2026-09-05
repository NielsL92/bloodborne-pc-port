"""Audit the callback/control continuation, preserving earlier recovery evidence."""
import collections
import hashlib
import json
from pathlib import Path
import sqlite3
import zipfile
from tools.cfg_recover_startup import sha,write_json

root=Path.cwd();before=root/'local/cfg/startup-recovery-v4';current=root/'local/cfg/startup-recovery-v7-repeat';repeat=root/'local/cfg/startup-recovery-v6'
identities={}
for name in ('analysis.sqlite','compilation-manifest.jsonl','frontier.jsonl','constructor-order.json'):
    digest=sha(current/name);assert digest==sha(repeat/name),name
    identities[name]=digest
for version in (2,3,4):
    assert sha(root/'local/cfg/derived-control-v1/candidates.json')==sha(root/f'local/cfg/derived-control-v{version}/candidates.json')
summary=json.loads((current/'summary.json').read_text())
assert summary['constructors']=={'decoded_with_explicit_boundaries':18444}
assert summary['counts']['recovery_entry']==21160 and summary['decode_issue_kinds']=={'fallthrough_at_fence':9}
db=sqlite3.connect(f'{(current/"analysis.sqlite").as_uri()}?mode=ro',uri=True)
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
missing=db.execute('SELECT DISTINCT q.module,q.target FROM recovery_request q LEFT JOIN recovery_entry e ON q.module=e.module AND q.target=e.start WHERE e.start IS NULL').fetchall();assert not missing
assert json.loads((current/'constructor-order.json').read_text())==json.loads((root/'local/cfg/startup-v1/roots.json').read_text())
artifacts={}
for key,path in dict(delta='local/cfg/startup-frontier-delta-v2/delta.json',
    derived='local/cfg/derived-control-checked-v1/contracts.json',
    ghidra_entry_only='local/cfg/ghidra-callback-closure-v1/summary.json',
    ghidra_with_lsda='local/cfg/ghidra-callback-closure-v2/summary.json',
    compilation='local/compiler-spike/callback-manifest-v1/summary.json').items():
    artifacts[key]=dict(path=path,sha256=sha(root/path),result=json.loads((root/path).read_text()))
derived=artifacts['derived']['result'];assert len(derived['contracts'])==28
assert derived['base_contracts_sha256']==sha(root/'tools/cfg_import_contracts.json')
assert derived['candidate_sha256']==sha(root/'local/cfg/derived-control-v2/candidates.json')
assert sum(r['shared_instructions'] for r in derived['ghidra_checks'])==254
assert sha(root/'local/cfg/derived-control-checked-v1/contracts.json')==sha(root/'local/cfg/derived-control-checked-v2/contracts.json')
# All newly requested entries and all remaining issues were independently checked.
ghidra=root/'local/cfg/ghidra-callback-closure-v2';comparisons=json.loads((ghidra/'comparison.json').read_text())
selected={(r['module'],r['start']) for r in comparisons}
delta=artifacts['delta']['result'];assert len(delta['added_entries'])==65
assert {(r['module'],r['entry']) for r in delta['added_entries']}<=selected
assert {(r['module'],r['entry']) for r in delta['remaining_issues']}<=selected
names=dict(db.execute('SELECT hash,name FROM module'));raw={};explained=[]
for row in comparisons:
    assert not row['boundary_disagreements'] and not row['only_recovery'],row
    if row['equal']:continue
    h,at=row['module'],row['start']
    if h not in raw:raw[h]={r['start']:r for r in json.loads((ghidra/names[h]/'ghidra.json').read_text())}
    ins={r['rva']:r for r in raw[h][at]['instructions']}
    sources=[]
    for pc,contract in db.execute("SELECT source,detail FROM recovery_edge WHERE module=? AND entry=? AND kind='annotated_control_contract_requires_runtime'",(h,at)):
        assert pc in ins and ins[pc]['flow']=='UNCONDITIONAL_CALL'
        sources.append(dict(source=pc,after=pc+ins[pc]['length'],contract=contract))
    queue=collections.deque(r['after'] for r in sources);seen=set()
    while queue:
        pc=queue.popleft()
        if pc in seen or pc not in ins:continue
        seen.add(pc);i=ins[pc];flow=i['flow']
        if 'JUMP' in flow:queue.extend(i['targets'])
        if flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow:queue.append(pc+i['length'])
    assert set(row['only_ghidra'])<=seen,row
    explained.append(dict(module=h,entry=at,extra_addresses=row['only_ghidra'],contracts=sources,
        classification='Independent Ghidra ordinary-call fallthrough after annotated nonreturn boundaries; LSDA roots supplied separately from expected instructions.'))
# Each built object must link to exactly the current manifest's instruction set.
compiler=root/'local/compiler-spike/callback-manifest-v1';compiled=json.loads((compiler/'results.json').read_text())
assert len(compiled)==65
for row in compiled:
    folder=compiler/row['folder'];unit=json.loads((folder/'manifest.json').read_text())
    ins=db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(unit['module_sha256'],unit['entry'])).fetchall()
    assert hashlib.sha256(json.dumps(ins,separators=(',',':')).encode()).hexdigest()==unit['instruction_set_sha256']
    if row['status']=='object_built':assert sha(folder/'function.obj')==row['object_sha256']
runs={}
for suffix in ('derived-control-v1','derived-control-v2','derived-control-v3','derived-control-v4','control-proof-checks-v1','ghidra-derived-control-v1','derived-control-check-v1','derived-control-check-v2','control-callback-checks-v1','control-callback-checks-v2','control-callback-checks-v3','startup-recovery-v6','startup-recovery-v7-repeat','startup-frontier-delta-v1','startup-frontier-delta-v2','ghidra-callback-closure-v1','ghidra-callback-closure-v2','callback-manifest-compile-v1'):
    name='20260905-p3-'+suffix;folder=root/'local/runs'/name;m=json.loads((folder/'manifest.json').read_text());assert m['status']=='pass',name
    with zipfile.ZipFile(folder/'sources.zip') as archive:
        for path,digest in m['source_sha256'].items():
            assert hashlib.sha256(archive.read(path.replace(chr(92),'/'))).hexdigest()==digest,(name,path)
    runs[name]=dict(status=m['status'],source_commit=m['project_commit'],elapsed_seconds=m['elapsed_seconds'],source_archive_sha256=sha(folder/'sources.zip'))
report=dict(status='startup closure continuation evidence consistency pass; P3 gate open',
    current_directory=str(current.relative_to(root)),summary=summary,reproducibility=identities,
    artifacts=artifacts,runs=runs,ghidra_disputes=dict(explained=explained,unresolved=[],
    all_new_entries_checked=True,all_remaining_boundary_entries_checked=True),
    compilation_rejections=[r for r in compiled if r['status']!='object_built'],
    limitations='The proof is conditional on exact ABI contracts, valid calls, supplied exception metadata, fixed binding and immutable code. Unknown indirect calls are deliberately rejected as proof paths. Callback ABI roles identify arguments; they do not prove runtime registrations or executions.',
    gate='P3 not passed: 9029 indirect-call records, 430 indirect-jump records, 9 fallthrough findings, 170 unresolved callback-argument records, runtime binding/registry/mutation, exception and native service/control contracts remain open. 52 new objects built; 12 sparse and 1 disputed entry explicitly excluded. No native game boot or playable port.',
    native_game_boot=False,native_port_playable=False)
write_json(root/'reports/startup-closure-evidence.json',report)
print(json.dumps(dict(status=report['status'],reproducibility=identities,ghidra_explained=len(explained),remaining_boundaries=9,compiled=artifacts['compilation']['result']['results'])),flush=True)
