"""Entry-driven static startup recovery; never an execution-coverage measurement.

Metadata supplies conservative decode fences, not function definitions. Explicit jumps
and calls cross fences as new entries; fallthrough across a fence is quarantined.
Callback/indirect constants are candidates under mutable-memory and ABI assumptions.
"""
from __future__ import annotations
import argparse
import bisect
import collections
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import time
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_GRP_CALL, CS_GRP_JUMP, CS_GRP_RET, CS_AC_WRITE
from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_OP_REG, X86_REG_RIP
from tools.formats import ElfImage


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def canonical_register(name):
    aliases = {'eax':'rax', 'ax':'rax', 'al':'rax', 'ah':'rax', 'ebx':'rbx', 'bx':'rbx', 'bl':'rbx', 'bh':'rbx',
               'ecx':'rcx', 'cx':'rcx', 'cl':'rcx', 'ch':'rcx', 'edx':'rdx', 'dx':'rdx', 'dl':'rdx', 'dh':'rdx',
               'edi':'rdi', 'di':'rdi', 'dil':'rdi', 'esi':'rsi', 'si':'rsi', 'sil':'rsi',
               'ebp':'rbp', 'bp':'rbp', 'bpl':'rbp', 'esp':'rsp', 'sp':'rsp', 'spl':'rsp'}
    if name.startswith('r') and name[-1:] in ('d', 'w', 'b') and name[1:-1].isdigit():
        return name[:-1]
    return aliases.get(name, name)


class Recovery:
    def __init__(self, source, roots_path, out, max_entries, max_instructions, jump_evidence=None):
        self.out, self.max_entries, self.max_instructions = out, max_entries, max_instructions
        out.mkdir(parents=True, exist_ok=False)
        shutil.copy2(source / 'analysis.sqlite', out / 'analysis.sqlite')
        self.db = sqlite3.connect(out / 'analysis.sqlite')
        self.db.executescript('''
            CREATE TABLE recovery_entry(module TEXT,start INTEGER,fence INTEGER,fence_reason TEXT,status TEXT,
              instructions INTEGER,issues INTEGER,PRIMARY KEY(module,start));
            CREATE TABLE recovery_instruction(module TEXT,rva INTEGER,size INTEGER,bytes TEXT,mnemonic TEXT,operands TEXT,
              PRIMARY KEY(module,rva));
            CREATE TABLE recovery_owner(module TEXT,entry INTEGER,rva INTEGER,PRIMARY KEY(module,entry,rva));
            CREATE TABLE recovery_edge(module TEXT,entry INTEGER,source INTEGER,target_module TEXT,target INTEGER,kind TEXT,detail TEXT);
            CREATE INDEX recovery_edges ON recovery_edge(module,entry);
            CREATE TABLE recovery_issue(module TEXT,entry INTEGER,rva INTEGER,kind TEXT,detail TEXT);
            CREATE INDEX recovery_issues ON recovery_issue(module,entry);
            CREATE TABLE recovery_reference(module TEXT,entry INTEGER,source INTEGER,target INTEGER,operation TEXT,write_access INTEGER);
            CREATE TABLE recovery_request(module TEXT,target INTEGER,reason TEXT,parent_module TEXT,parent_entry INTEGER,source INTEGER);
        ''')
        self.decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        self.decoder.detail = True
        self.images, self.links, self.relocs, self.ranges, self.fences = {}, {}, {}, {}, {}
        self.names, self.executable, self.exports, self.pads, self.regions = {}, {}, collections.defaultdict(list), {}, {}
        self.code_seeds = {}
        self.queue, self.requested, self.done = collections.deque(), set(), set()
        self.byte_owners = collections.defaultdict(dict)
        self.known = collections.defaultdict(list)
        for h, src, dst in self.db.execute('SELECT module,source,target FROM edge ORDER BY module,source,target'):
            self.known[h, src].append(dst)
        self.symbol_names = {r['nid']: r.get('resolved_name') for r in json.loads(Path('local/analysis/imports.json').read_text())}
        for h, path, name in self.db.execute('SELECT hash,path,name FROM module ORDER BY name'):
            assert sha(path) == h
            im = self.images[h] = ElfImage(Path(path).read_bytes())
            link = self.links[h] = im.linkage()
            self.names[h] = name
            self.relocs[h] = {r['offset']:r for r in link['relocations']}
            self.executable[h] = [(s.vaddr, s.vaddr+s.filesz) for s in im.segments if s.type in (1, 0x61000010) and s.flags & 1]
            rr = self.db.execute('SELECT start,size FROM unwind_range WHERE module=? ORDER BY start', (h,)).fetchall()
            self.ranges[h] = ([r[0] for r in rr], dict(rr))
            self.fences[h] = sorted({r[0] for r in self.db.execute('SELECT rva FROM seed WHERE module=?', (h,))})
            self.code_seeds[h] = set(self.fences[h])
            for s in link['symbols']:
                if s['defined'] and s['type'] == 2:
                    self.exports[tuple(s[k] for k in ('nid','library','module'))].append((h,s['value']))
            for start, size, slot in self.db.execute('SELECT start,size,personality_slot FROM exception_region WHERE module=?', (h,)):
                self.regions[h,start] = (size,slot)
                self.pads[h,start] = sorted({r[0] for r in self.db.execute('SELECT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL', (h,start))})
        annotations = json.loads(Path('tools/cfg_import_contracts.json').read_text())
        self.contracts = {tuple(c[k] for k in ('nid','library','module')):c for c in annotations['contracts']}
        self.local_contracts = {}
        for c in annotations['contracts']:
            for e in c.get('local_entries', []) + [e for e in c['evidence'] if e['kind']=='supplied module static implementation']:
                assert hashlib.sha256(self.images[e['module_sha256']].at_va(e['rva'],e['size'])).hexdigest() == e['code_sha256']
            for e in c.get('local_entries', []):
                self.local_contracts[e['module_sha256'],e['rva']] = c
        self.static_tables = set()
        if jump_evidence:
            table_evidence = json.loads(jump_evidence.read_text())
            assert table_evidence['status']=='independent static table comparison passed'
            for row in table_evidence['entries']:
                h=row['module_sha256'];im=self.images[h]
                assert hashlib.sha256(im.at_va(row['table_rva'],row['count']*4)).hexdigest()==row['table_sha256']
                assert im.at_va(row['guard_rva'],len(bytes.fromhex(row['guard_bytes']))).hex()==row['guard_bytes']
                self.known[h,row['branch']]=sorted(set(row['targets']))
                self.static_tables.add((h,row['branch']))
        self.import_cache = {}
        self.roots = json.loads(roots_path.read_text())
        self.main = next(h for h,n in self.names.items() if n=='eboot.bin')
        assert self.roots == [dict(ordinal=o,slot=s,target=t,evidence=e,indexed_unwind_start=t in self.ranges[self.main][1])
                              for o,s,t,e in self.db.execute('SELECT ordinal,slot,target,evidence FROM initializer_slot WHERE module=? ORDER BY ordinal',(self.main,))]
        self.identity = dict(schema=1, source_db_sha256=sha(source/'analysis.sqlite'), roots_sha256=sha(roots_path),
            control_contracts_sha256=sha('tools/cfg_import_contracts.json'), modules=self.names,
            max_entries=max_entries, max_instructions_per_entry=max_instructions, jump_evidence_sha256=sha(jump_evidence) if jump_evidence else None,
            policy='Static overapproximation. Next metadata seed/unwind end is a decode fence, not a proven function end. Calls/explicit jumps expand; fallthrough at fences is quarantined. Constant callbacks and relocated slots remain candidates; only independently seeded addresses are expanded from those candidates. No game CPU execution.')
        write_json(out/'identity.json', self.identity)
        for r in self.roots:
            self.request(self.main,r['target'],'ordered_initial_constructor',self.main,0x20,0x82)
        self.request(self.main,0xa0,'actual_entry')
        self.request(self.main,0x20,'initializer')
        for h, im in self.images.items():
            if h == self.main: continue
            for tag,val in im.dynamic():
                if tag==12 and self.is_code(h,val):
                    self.request(h,val,'bundled_DT_INIT_order_unvalidated')

    def is_code(self, h, address):
        return address is not None and any(a<=address<b for a,b in self.executable[h])

    def request(self,h,target,reason,parent=None,entry=None,source=None):
        self.db.execute('INSERT INTO recovery_request VALUES(?,?,?,?,?,?)',(h,target,reason,parent,entry,source))
        if (h,target) not in self.requested:
            self.requested.add((h,target))
            self.queue.append((h,target))

    def imported(self,h,target):
        key=(h,target)
        if key in self.import_cache: return self.import_cache[key]
        self.import_cache[key]=None
        if not self.is_code(h,target): return None
        try: i=next(self.decoder.disasm(self.images[h].at_va(target,15),target,count=1),None)
        except Exception: return None
        if not i or i.mnemonic!='jmp' or i.operands[0].type!=X86_OP_MEM or i.operands[0].mem.base!=X86_REG_RIP: return None
        r=self.relocs[h].get(target+i.size+i.operands[0].mem.disp)
        if not r or r['type']!=7:return None
        s=dict(self.links[h]['symbols'][r['symbol']])
        s['resolved_name']=self.symbol_names.get(s['nid'])
        self.import_cache[key]=s
        return s

    def fence(self,h,start):
        segment_end=next((b for a,b in self.executable[h] if a<=start<b),None)
        if segment_end is None: return start,'non_executable_or_unbacked'
        starts,ranges=self.ranges[h]
        index=bisect.bisect_right(starts,start)-1
        if index>=0 and start<starts[index]+ranges[starts[index]]:
            return min(segment_end,starts[index]+ranges[starts[index]]),'unwind_end_is_analysis_fence'
        seeds=self.fences[h]
        index=bisect.bisect_right(seeds,start)
        return min(segment_end,seeds[index] if index<len(seeds) else segment_end),'next_seed_or_segment_end_is_analysis_fence'

    def recover(self,h,start):
        end,reason=self.fence(h,start)
        insns,edges,issues,refs={},[],[],[]
        byte_owners=self.byte_owners[h]
        def issue(at,kind,detail):issues.append((at,kind,str(detail)))
        def edge(at,target,kind,detail='',other=None):edges.append((at,other or h,target,kind,detail))
        def dependency(at,target,kind,detail='',other=None):
            other=other or h
            edge(at,target,kind,detail,other)
            if kind in ('callback_argument_candidate','indirect_target_candidate') and target not in self.code_seeds[other]:
                return  # Executable mappings also contain strings/data; retain the edge without promoting it.
            self.request(other,target,kind,h,start,at)
        def transfer(at,target,kind):
            imp=self.imported(h,target)
            c=self.local_contracts.get((h,target))
            if imp:
                key=tuple(imp[k] for k in ('nid','library','module'))
                c=self.contracts.get(key)
                edge(at,target,'import_contract_unvalidated',json.dumps(imp,sort_keys=True))
                for other,dst in self.exports.get(key,[]): dependency(at,dst,'bundled_export_candidate',json.dumps(imp,sort_keys=True),other)
            else: dependency(at,target,kind)
            if c:
                edge(at,target,'annotated_control_contract_requires_runtime',c['id'])
                if c['restored_target_unknown']:edge(at,None,c.get('unknown_exit_kind','unresolved_restored_context'),c['id'])
            return c
        queue=collections.deque([start]+self.pads.get((h,start),[]))
        if end==start:
            issue(start,'non_executable_or_unbacked_entry','target not decoded');queue.clear()
        if (h,start) in self.regions:
            size,slot=self.regions[h,start]
            edge(start,None,'exception_runtime_unvalidated',json.dumps(dict(personality_slot=slot,lsda_owner=start)))
            if slot is not None:
                r=self.relocs[h].get(slot)
                if r and r['type']==8: dependency(start,r['addend'],'exception_personality_candidate')
                elif r and r['type'] in (1,6,7):
                    s=self.links[h]['symbols'][r['symbol']]
                    edge(start,None,'personality_import_unvalidated',json.dumps(s,sort_keys=True))
                    for other,dst in self.exports.get(tuple(s[k] for k in ('nid','library','module')),[]):dependency(start,dst,'exception_personality_candidate','',other)
                else:edge(start,None,'unresolved_personality',str(slot))
        # Each worklist item starts with unknown registers: no path-insensitive merge.
        while queue:
            address=queue.popleft();values={}
            while start<=address<end:
                if address in insns:break
                if len(insns)>=self.max_instructions:
                    issue(address,'instruction_budget','entry truncated');queue.clear();break
                if address in byte_owners and byte_owners[address]!=address:
                    issue(address,'overlapping_decode_target',hex(byte_owners[address]));break
                try: raw=self.images[h].at_va(address,min(15,end-address))
                except Exception as e:issue(address,'unreadable_instruction',e);break
                i=next(self.decoder.disasm(raw,address,count=1),None)
                if not i or address+i.size>end:issue(address,'undecodable_or_crosses_fence',raw.hex());break
                conflicts={byte_owners[b] for b in range(address,address+i.size) if b in byte_owners and byte_owners[b]!=address}
                if conflicts:issue(address,'overlapping_decode_bytes',json.dumps(sorted(conflicts)));break
                insns[address]=i
                for b in range(address,address+i.size):byte_owners[b]=address
                after=address+i.size
                for op in i.operands:
                    if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                        target=after+op.mem.disp;written=bool(op.access & CS_AC_WRITE)
                        refs.append((address,target,i.mnemonic,int(written)))
                        if written and self.is_code(h,target):edge(address,target,'possible_code_write',i.op_str)
                        if written and h==self.main and 87817048<=target<87972672:edge(address,target,'possible_constructor_table_write',i.op_str)
                is_call,is_jump=i.group(CS_GRP_CALL),i.group(CS_GRP_JUMP)
                if i.group(CS_GRP_RET):edge(address,None,'logical_return_requires_dispatch',i.mnemonic);break
                if i.mnemonic in ('iret','iretq','sysret','sysretq','ud2','hlt'):
                    edge(address,None,'service_or_trap_boundary',i.mnemonic);break
                if i.mnemonic in ('syscall','int','int3'):
                    edge(address,None,'service_or_trap_boundary',i.mnemonic)
                if is_call or is_jump:
                    target=i.operands[0].imm if i.operands[0].type==X86_OP_IMM else None
                    if is_call:
                        for reg in ('rdi','rsi','rdx','rcx','r8','r9'):
                            value=values.get(reg)
                            if value and self.is_code(h,value[0]):
                                dependency(address,value[0],'callback_argument_candidate',json.dumps(dict(register=reg,provenance=value[1],abi='SysV candidate; callee semantics not established')))
                    if target is not None:
                        if is_call:
                            if transfer(address,target,'direct_call'):break
                        elif start<=target<end:
                            edge(address,target,'direct_jump');queue.append(target)
                        else:transfer(address,target,'cross_fence_jump')
                    elif (h,address) in self.known:
                        for dst in self.known[h,address]:
                            edge(address,dst,'independently_recovered_jump_table' if (h,address) in self.static_tables else 'validated_jump_table')
                            if start<=dst<end:queue.append(dst)
                            else:self.request(h,dst,'validated_jump_table',h,start,address)
                    else:
                        edge(address,None,'unresolved_indirect_call' if is_call else 'unresolved_indirect_jump',i.op_str)
                        op=i.operands[0];candidate=None;why=None
                        if op.type==X86_OP_REG and canonical_register(i.reg_name(op.reg)) in values:
                            candidate,why=values[canonical_register(i.reg_name(op.reg))]
                        elif op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                            slot=after+op.mem.disp;r=self.relocs[h].get(slot)
                            if r and r['type']==8:candidate,why=r['addend'],f'initial relocated mutable slot {slot:#x}'
                        if self.is_code(h,candidate):dependency(address,candidate,'indirect_target_candidate',str(why))
                    if is_jump and i.mnemonic in ('jmp','ljmp'):break
                    values.clear()
                    edge(address,after,'fallthrough')
                    if after==end:issue(address,'fallthrough_at_fence',i.mnemonic)
                    address=after
                    if is_jump:
                        queue.append(after);break
                    continue
                # Local constant propagation is only a candidate generator. Partial-register
                # writes invalidate the entire value; memory loads are never treated immutable.
                new=None
                if len(i.operands)>=2 and i.operands[0].type==X86_OP_REG and i.operands[0].size in (4,8):
                    dst,src=i.operands[:2];reg=canonical_register(i.reg_name(dst.reg))
                    if i.mnemonic in ('mov','movabs'):
                        if src.type==X86_OP_IMM:new=(reg,src.imm,[address])
                        elif src.type==X86_OP_REG and canonical_register(i.reg_name(src.reg)) in values:
                            value,prov=values[canonical_register(i.reg_name(src.reg))];new=(reg,value,prov+[address])
                    elif i.mnemonic=='lea' and src.type==X86_OP_MEM and src.mem.base==X86_REG_RIP:
                        new=(reg,after+src.mem.disp,[address])
                    elif i.mnemonic in ('add','sub') and src.type==X86_OP_IMM and reg in values:
                        value,prov=values[reg];new=(reg,value+(src.imm if i.mnemonic=='add' else -src.imm),prov+[address])
                    if new and dst.size==4:new=(new[0],new[1]&0xffffffff,new[2])
                for reg in i.regs_access()[1]:values.pop(canonical_register(i.reg_name(reg)),None)
                if new:values[new[0]]=(new[1],new[2])
                edge(address,after,'fallthrough')
                if after==end:issue(address,'fallthrough_at_fence',i.mnemonic)
                address=after
        for address,i in sorted(insns.items()):
            self.db.execute('INSERT OR IGNORE INTO recovery_instruction VALUES(?,?,?,?,?,?)',(h,address,i.size,i.bytes.hex(),i.mnemonic,i.op_str))
            self.db.execute('INSERT INTO recovery_owner VALUES(?,?,?)',(h,start,address))
        self.db.executemany('INSERT INTO recovery_edge VALUES(?,?,?,?,?,?,?)',[(h,start,*e) for e in edges])
        self.db.executemany('INSERT INTO recovery_issue VALUES(?,?,?,?,?)',[(h,start,*e) for e in issues])
        self.db.executemany('INSERT INTO recovery_reference VALUES(?,?,?,?,?,?)',[(h,start,*e) for e in refs])
        status='quarantined_decode_issues' if issues else 'decoded_with_explicit_boundaries'
        self.db.execute('INSERT INTO recovery_entry VALUES(?,?,?,?,?,?,?)',(h,start,end,reason,status,len(insns),len(issues)))

    def run(self):
        begin=time.monotonic()
        while self.queue and len(self.done)<self.max_entries:
            h,start=self.queue.popleft()
            self.recover(h,start);self.done.add((h,start))
            if len(self.done)%1000==0:
                self.db.commit()
                print(json.dumps(dict(entries=len(self.done),queued=len(self.queue),seconds=time.monotonic()-begin)),flush=True)
        # Seed initializer's known initial slots without claiming runtime immutability.
        for r in self.roots:
            self.db.execute('INSERT INTO recovery_edge VALUES(?,?,?,?,?,?,?)',(self.main,0x20,0x82,self.main,r['target'],'initial_constructor_target',json.dumps(r,sort_keys=True)))
        self.db.commit()
        self.export()

    def export(self):
        db=self.db
        roots_by_target={r['target']:r['ordinal'] for r in self.roots}
        frontier=collections.Counter()
        units=0
        with (self.out/'compilation-manifest.jsonl').open('w',encoding='utf-8') as manifest, (self.out/'frontier.jsonl').open('w',encoding='utf-8') as unresolved:
            for h,start,end,reason,status,count,nissues in db.execute('SELECT * FROM recovery_entry ORDER BY module,start'):
                rows=db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON o.module=i.module AND o.rva=i.rva WHERE o.module=? AND o.entry=? ORDER BY i.rva',(h,start)).fetchall()
                edges=[dict(source=a,target_module=b,target=c,kind=d,detail=e) for a,b,c,d,e in db.execute("SELECT source,target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=? AND kind!='fallthrough' ORDER BY source,kind,target",(h,start))]
                issues=[dict(rva=a,kind=b,detail=c) for a,b,c in db.execute('SELECT rva,kind,detail FROM recovery_issue WHERE module=? AND entry=? ORDER BY rva,kind',(h,start))]
                unit=dict(module_sha256=h,module=self.names[h],entry=start,constructor_ordinal=roots_by_target.get(start) if h==self.main else None,
                    fence=end,fence_reason=reason,decode_status=status,compilation_status='not_compiled',execution_status='not_executed',
                    instructions=[dict(rva=a,size=b,bytes=c) for a,b,c in rows],edges=edges,issues=issues,
                    instruction_set_sha256=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest())
                manifest.write(json.dumps(unit,separators=(',',':'))+'\n');units+=1
                if units%1000==0: print(json.dumps(dict(manifest_units=units)),flush=True)
                for e in edges:
                    if e['kind'] not in ('direct_call','direct_jump','cross_fence_jump','validated_jump_table','initial_constructor_target','bundled_export_candidate'):
                        unresolved.write(json.dumps(dict(module=h,entry=start,**e),separators=(',',':'))+'\n');frontier[e['kind']]+=1
                for e in issues:
                    unresolved.write(json.dumps(dict(module=h,entry=start,**e),separators=(',',':'))+'\n');frontier[e['kind']]+=1
            for h,target in self.queue:
                unresolved.write(json.dumps(dict(module=h,target=target,kind='entry_budget_not_decoded'))+'\n');frontier['entry_budget_not_decoded']+=1
        counts={table:db.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ('recovery_entry','recovery_instruction','recovery_edge','recovery_issue','recovery_request')}
        constructors=dict(db.execute("SELECT status,count(*) FROM recovery_entry WHERE module=? AND start IN (SELECT target FROM initializer_slot WHERE module=?) GROUP BY status",(self.main,self.main)))
        modules={self.names[h]:n for h,n in db.execute('SELECT module,count(*) FROM recovery_entry GROUP BY module')}
        issues=dict(db.execute('SELECT kind,count(*) FROM recovery_issue GROUP BY kind'))
        write_json(self.out/'constructor-order.json',self.roots)
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        db.commit();db.close()
        summary=dict(status='P3 startup compilation/control closure NOT passed',counts=counts,constructors=constructors,modules=modules,
            decode_issue_kinds=issues,frontier_counts=dict(frontier),queued=len(self.queue),
            manifest_units=units,db_sha256=sha(self.out/'analysis.sqlite'),manifest_sha256=sha(self.out/'compilation-manifest.jsonl'),
            limitations=self.identity['policy'],native_game_boot=False,native_port_playable=False)
        write_json(self.out/'summary.json',summary)
        print(json.dumps(summary),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('out',type=Path)
    p.add_argument('--source',type=Path,default=Path('local/cfg/startup-db-v1'))
    p.add_argument('--roots',type=Path,default=Path('local/cfg/startup-v1/roots.json'))
    p.add_argument('--jump-evidence',type=Path)
    p.add_argument('--max-entries',type=int,default=100000)
    p.add_argument('--max-instructions',type=int,default=100000)
    a=p.parse_args()
    Recovery(a.source,a.roots,a.out,a.max_entries,a.max_instructions,a.jump_evidence).run()


if __name__=='__main__':main()
