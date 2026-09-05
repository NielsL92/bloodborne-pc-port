"""Cross-check each derived control summary against independent Ghidra flow."""
import argparse
import json
from pathlib import Path
import sqlite3
from tools.cfg_derive_control import prove
from tools.cfg_recover_startup import sha, write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('derived',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    data=json.loads(a.derived.read_text());assert data['source_db_sha256']==sha(a.source/'analysis.sqlite')
    assert data['base_contracts_sha256']==sha('tools/cfg_import_contracts.json')
    db=sqlite3.connect(f'{(a.source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
    names=dict(db.execute('SELECT hash,name FROM module'));raw={};checks=[]
    ghidra_summary=json.loads((a.ghidra/'summary.json').read_text())
    assert ghidra_summary['source_db_sha256']==data['source_db_sha256']
    for row in data['contracts']:
        h,at=row['module_sha256'],row['rva']
        if h not in raw:raw[h]={r['start']:r for r in json.loads((a.ghidra/names[h]/'ghidra.json').read_text())}
        ins={r['rva']:r for r in raw[h][at]['instructions']};nodes={}
        terminals={int(pc) for pc in row['terminals']}
        for pc,r in ins.items():
            flow=r['flow']
            if 'COMPUTED' in flow or 'TERMINATOR' in flow:
                nodes[pc]=None
            elif 'JUMP' in flow:
                nodes[pc]=r['targets']+([] if flow=='UNCONDITIONAL_JUMP' else [pc+r['length']])
            else:nodes[pc]=[pc+r['length']]
        for pc,size,b in row['instructions']:
            assert pc in ins and (size,b)==(ins[pc]['length'],ins[pc]['bytes']), (h,at,pc)
        for pc in terminals:
            assert ins[pc]['flow'] in ('UNCONDITIONAL_CALL','UNCONDITIONAL_JUMP'),ins[pc]
            assert len(ins[pc]['targets'])==1
            targets={r[0] for r in db.execute("SELECT target FROM recovery_edge WHERE module=? AND entry=? AND source=? AND kind IN ('direct_call','cross_fence_jump','import_contract_unvalidated')",(h,at,pc))}
            assert ins[pc]['targets'][0] in targets, 'independent terminal target mismatch'
        visited=prove(nodes,row['roots'],terminals)
        assert visited==[r[0] for r in row['instructions']], (h,at,visited)
        checks.append(dict(module_sha256=h,entry=at,shared_instructions=len(visited),
            ghidra_extra_instructions=sorted(set(ins)-set(visited)),
            classification='Exact independent instruction identities and CFG paths under the same explicit terminal contracts; extra ordinary fallthrough remains raw evidence.'))
    data.update(status='independent Ghidra control comparison passed',ghidra_checks=checks,
        candidate_sha256=sha(a.derived),ghidra_comparison_sha256=sha(a.ghidra/'comparison.json'),
        ghidra_raw_sha256={names[h]:sha(a.ghidra/names[h]/'ghidra.json') for h in raw})
    write_json(a.out/'contracts.json',data)
    print(json.dumps(dict(status=data['status'],contracts=len(checks),instructions=sum(c['shared_instructions'] for c in checks))),flush=True)

if __name__=='__main__':main()
