"""Validate source/request pairs without granting native target dispatch."""
import argparse,collections,json
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_INT,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('active',type=Path);p.add_argument('inventory',type=Path);p.add_argument('linkage',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
active=read(a.active);rows=read(a.inventory/'sourced-control-sites.json');roots={pc for r in active for pc in r['compiled_roots']};imports={r['logical_address']:r for r in read(a.linkage/'unresolved-symbols.json') if r['kind']=='import PLT requires native binding'};decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;grouped=collections.defaultdict(list)
for row in rows:grouped[row['object']].append(row)
# Tail-only PLT stubs do not create undefined COFF function symbols.
tail_only=[]
for row in read(a.linkage/'explicit-missing-blocks.json'):
 if 'import_stub_evidence' not in row:continue
 pc=row['logical_address'];evidence=row['import_stub_evidence'];assert evidence['relocation']['type']==7
 if pc in imports:
  assert imports[pc]['stub_bytes']==evidence['bytes'] and imports[pc]['relocation']==evidence['relocation'] and imports[pc]['symbol_record']==evidence['symbol']
 else:
  imports[pc]=dict(logical_address=pc,module=row['module'],rva=row['rva'],kind='import PLT requires native binding',stub_bytes=evidence['bytes'],relocation=evidence['relocation'],symbol_record=evidence['symbol'],runtime_binding_validated=False,coff_undefined_symbol=False);tail_only.append(pc)
write_json(a.out/'native-import-stubs.json',[imports[pc] for pc in sorted(imports)])
windows=[]
for pc in tail_only:
 record=imports[pc];windows.append(dict(module=record['module'],start=record['rva'],end=record['rva']+len(record['stub_bytes'])//2))
write_json(a.out/'ghidra-tail-windows.json',windows)
pairs={};fault_counts=collections.Counter();unreachable=collections.Counter();site_count=0
for index,sites in grouped.items():
 obj=active[index];folder=Path('local/compiler-spike')/obj['source_batch']/obj['folder'];data=read(folder/'input.json');instructions={i['address']:i['bytes'] for i in data['instructions']};audit=read(folder/'audit.json');assert sha(folder/'function.obj')==obj['object_sha256'];guard_map={(r['root'],r['source']):r for r in audit['call_return_checks']};forbidden={r['address'] for r in data['return_contracts']}
 for site in sites:
  if not site['cfg_reachable_from_entry']:unreachable[site['callee']]+=1;continue
  args=site['arguments'];assert site['nounwind']
  if site['callee']=='__bb_native_control_fault':
   assert site['noreturn'] and len(args)==6;assert all(args[n]['integer_origins_complete'] and len(args[n]['possible_integer_values_hex'])==1 for n in [1,3,4]);source=int(args[1]['possible_integer_values_hex'][0],16);reason=int(args[3]['possible_integer_values_hex'][0],16);wanted=int(args[4]['possible_integer_values_hex'][0],16);guard=guard_map[site['function'],source];assert wanted==guard['expected_next_pc'];assert reason==(2 if guard['no_normal_return'] else 3 if guard['kind']=='asynchronous-hypercall' else 1);fault_counts[reason]+=1;continue
  assert len(args)==5 and not site['noreturn'];assert args[3]['integer_origins_complete'] and args[4]['integer_origins_complete'] and len(args[4]['possible_integer_values_hex'])==1;target=int(args[4]['possible_integer_values_hex'][0],16);site_count+=1
  for value in args[3]['possible_integer_values_hex']:
   source=int(value,16);assert source in instructions and source not in forbidden;code=instructions[source];ins=next(decoder.disasm(bytes.fromhex(code),source,count=1));assert ins.size*2==len(code);next_pc=source+ins.size;kind=None
   if ins.group(CS_GRP_CALL):
    if len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM and ins.operands[0].imm==next_pc:kind='call-next sequence'
    else:guard=guard_map[site['function'],source];assert not guard['no_normal_return'] and guard['expected_next_pc']==target;kind='checked ordinary call continuation'
    assert target==next_pc
   elif ins.group(CS_GRP_JUMP):
    assert len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM
    if target==ins.operands[0].imm:kind='decoded direct branch'
    else:assert ins.mnemonic!='jmp' and target==next_pc;kind='decoded conditional fallthrough'
   elif ins.group(CS_GRP_INT):
    guard=guard_map[site['function'],source];assert guard['kind']=='asynchronous-hypercall' and guard['expected_next_pc']==target;kind='checked hypercall continuation'
   else:assert not ins.group(CS_GRP_RET) and target==next_pc;kind='decoded ordinary fallthrough'
   target_kind='compiled root' if target in roots else 'verified import stub' if target in imports else 'unresolved target';key=source,target
   row=pairs.setdefault(key,dict(source=source,requested_target=target,source_bytes=code,instruction=ins.mnemonic+' '+ins.op_str,edge_kind=kind,target_kind=target_kind,compiled_owners=[],native_dispatch_validated=False));assert row['source_bytes']==code and row['edge_kind']==kind;owner=dict(object=index,function=site['function'])
   if owner not in row['compiled_owners']:row['compiled_owners'].append(owner)
records=[pairs[key] for key in sorted(pairs)];write_json(a.out/'source-target-pairs.json',records);summary=dict(status='source/request pairs independently decoded; native dispatch still requires validation',active_manifest_sha256=sha(a.active),inventory_sha256=sha(a.inventory/'summary.json'),reachable_transfer_sites=site_count,unique_pairs=len(records),runtime_import_stubs=len(imports),tail_only_import_stubs=[imports[pc] for pc in tail_only],runtime_import_registry_sha256=sha(a.out/'native-import-stubs.json'),target_classes=dict(collections.Counter(r['target_kind'] for r in records)),edge_classes=dict(collections.Counter(r['edge_kind'] for r in records)),reachable_fault_reasons=dict(fault_counts),structurally_unreachable_sites=dict(unreachable),pairs_sha256=sha(a.out/'source-target-pairs.json'),runtime_requirements=['Actual target must equal the compiler requested target.','Source/request pair must match the exact compiled input and module code identities.','Target must resolve to a compiled root or a separately validated native import binding; unresolved targets fail explicitly.','Conditional recovery assumptions, mutable data and unknown call/callback/exception targets remain visible.'],p3_gate_passed=False,game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
