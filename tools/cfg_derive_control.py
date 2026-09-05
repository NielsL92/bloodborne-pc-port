"""Derive conditional no-ordinary-return summaries from explicit recovered CFGs.

This is a least fixed point over already documented ABI contracts, never an
inference from the last instruction or an unwind extent. Cycles, unresolved
indirect control, service boundaries and uncovered successors reject a proof.
All metadata landing pads are additional roots. Ordinary calls still require
their ABI and exception behavior to be implemented by the native runtime.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sqlite3
from tools.cfg_recover_startup import sha, write_json


def prove(nodes, roots, terminals):
    """Return visited nodes only if every finite path reaches a known terminal.

    Nodes map addresses to explicit local successors, or None for a rejection.
    A cycle is deliberately inconclusive; it cannot establish a new contract.
    """
    active, done = set(), set()
    def visit(at):
        if at in done: return True
        if at in active or at not in nodes: return False
        if at in terminals:
            done.add(at); return True
        successors = nodes[at]
        if not successors: return False
        active.add(at)
        ok = all(visit(dst) for dst in successors)
        active.remove(at)
        if ok: done.add(at)
        return ok
    try:
        return sorted(done) if all(visit(at) for at in roots) else None
    except RecursionError:
        return None  # Bounded analysis; never assume a long path terminates.


def model_nodes(h, rows, edges, known_local, known_import):
    nodes, terminals, evidence = {}, set(), {}
    for pc, size, raw, mnemonic in rows:
        es = edges[pc];contracts = set()
        for other, dst, kind, detail in es:
            if kind == 'annotated_control_contract_requires_runtime': contracts.add(detail)
            if kind in ('direct_call', 'cross_fence_jump'): contracts.update(known_local.get((other, dst), []))
            if kind == 'import_contract_unvalidated':
                symbol = json.loads(detail)
                contracts.update(known_import.get(tuple(symbol[k] for k in ('nid', 'library', 'module')), []))
        nodes[pc] = [dst for other, dst, kind, _ in es if kind in ('fallthrough', 'direct_jump') and other == h]
        if any(kind in ('unresolved_indirect_call', 'unresolved_indirect_jump', 'service_or_trap_boundary', 'logical_return_requires_dispatch', 'possible_code_write') for _, _, kind, _ in es):
            nodes[pc] = None
        elif contracts and mnemonic in ('call','jmp','ljmp'):
            terminals.add(pc);evidence[pc]=sorted(contracts)
        elif any(kind == 'cross_fence_jump' or (kind=='import_contract_unvalidated' and mnemonic!='call') for _,_,kind,_ in es):
            # A conditional external transfer has two alternatives. Reject it
            # here rather than silently dropping its nonlocal successor.
            nodes[pc] = None
    return nodes,terminals,evidence


def derive(source, out):
    identity=json.loads((source/'identity.json').read_text())
    if identity.get('derived_control_sha256'):
        raise ValueError('Input already uses derived summaries: explicitly import and verify their transitive evidence before extending this experiment.')
    assert identity['control_contracts_sha256']==sha('tools/cfg_import_contracts.json'), 'source base contract identity changed'
    out.mkdir(parents=True, exist_ok=False)
    db = sqlite3.connect(f'{(source/"analysis.sqlite").resolve().as_uri()}?mode=ro', uri=True)
    base = json.loads(Path('tools/cfg_import_contracts.json').read_text())
    known_local = {(e['module_sha256'], e['rva']): [c['id']] for c in base['contracts'] for e in c.get('local_entries', [])}
    known_import = {tuple(c[k] for k in ('nid', 'library', 'module')): [c['id']] for c in base['contracts']}
    exports = collections.defaultdict(list)
    for h, at, nid, lib, provider in db.execute('SELECT module,rva,nid,library,provider FROM symbol WHERE defined=1 AND type=2'):
        exports[h, at].append((nid, lib, provider))
    # Targeted investigation of callees at every disputed final call, plus
    # supplied libc throw helpers which anchor most of those call chains.
    candidates = set(db.execute("SELECT DISTINCT e.target_module,e.target FROM recovery_issue q JOIN recovery_edge e ON q.module=e.module AND q.entry=e.entry AND q.rva=e.source WHERE e.kind IN ('direct_call','bundled_export_candidate')"))
    libc = db.execute("SELECT hash FROM module WHERE name='libc.prx'").fetchone()[0]
    candidates.update((libc, at) for at in (0x5ecb0, 0x5ed50, 0x5ee90))
    units = {}
    for h, at in sorted(candidates):
        rows = db.execute('SELECT i.rva,i.size,i.bytes,i.mnemonic FROM recovery_owner o CROSS JOIN recovery_instruction i ON o.module=i.module AND o.rva=i.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva', (h, at)).fetchall()
        edges = collections.defaultdict(list)
        for src, other, dst, kind, detail in db.execute('SELECT source,target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=?', (h, at)):
            edges[src].append((other, dst, kind, detail))
        pads = [r[0] for r in db.execute('SELECT DISTINCT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL ORDER BY landing_pad', (h, at))]
        units[h, at] = (rows, edges, [at] + pads)
    proofs = {}
    iteration = 0
    while True:
        added = []
        for (h, at), (rows, edges, roots) in sorted(units.items()):
            if (h, at) in known_local or not rows: continue
            nodes,terminals,evidence=model_nodes(h,rows,edges,known_local,known_import)
            visited = prove(nodes, roots, terminals)
            if visited is None: continue
            used = {pc: evidence[pc] for pc in visited if pc in terminals}
            if not used: continue
            ident = f'derived-{h[:12]}-{at:x}'
            instructions = [[pc, size, raw] for pc, size, raw, _ in rows if pc in visited]
            added.append(((h, at), dict(id=ident, module_sha256=h, rva=at,
                iteration=iteration, roots=roots, terminals=used,
                instructions=instructions, instruction_set_sha256=hashlib.sha256(json.dumps(instructions,separators=(',', ':')).encode()).hexdigest(),
                import_keys=sorted(exports[h, at]),
                dependencies=sorted({c for cs in used.values() for c in cs}),
                contract='No ordinary return under listed transitive ABI/control contracts; exception destinations and runtime binding remain unvalidated.')))
        if not added: break
        for key, row in added:
            proofs[key] = row; known_local[key] = [row['id']]
            for imp in exports[key]: known_import[imp] = [row['id']]
        iteration += 1
    result = dict(schema=1, status='derived candidates require independent Ghidra check',
        source_db_sha256=sha(source/'analysis.sqlite'), base_contracts_sha256=sha('tools/cfg_import_contracts.json'),
        candidates=len(candidates), iterations=iteration, contracts=[proofs[k] for k in sorted(proofs)],
        rejected=[dict(module=h,entry=at) for h,at in sorted(candidates-set(proofs))],
        limitations='Conditional static CFG proof only. No execution or complete function-boundary proof. Unknown indirect edges, cycles and missing successors are inconclusive. Library binding, code immutability, ordinary-call ABI and exception metadata/runtime are assumptions.')
    write_json(out/'candidates.json', result)
    write_json(out/'selection.json', [dict(module=h,start=at,reason='derived_control_dispute') for h,at in sorted(proofs)])
    print(json.dumps(dict(candidates=len(candidates),derived=len(proofs),iterations=iteration,rejected=len(result['rejected']))), flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    derive(a.source,a.out)
