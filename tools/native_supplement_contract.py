"""Check the distinct evidence contracts for leaf fixtures and static CFG supplements."""
import json
from pathlib import Path

def validate(summary, folder):
 count=len(summary['compiled_roots']);kind=summary.get('validation_kind')
 if kind!='independent-cfg-compilation':
  assert summary['status']=='supplemental supplied leaf compiled and native semantics checked';assert 1<=count<=16;assert kind=='conditional-simple-leaf-batch' or count==1;assert summary.get('cases_per_root',3072)==3072 and summary['positive']['cases']==3072*count and summary['negative_stops']==2*count
  # Grouped fixtures have two negative checks per root.
  return
 assert summary['status']=='supplied CFG compiled with independently checked boundaries' and 1<=count<=64 and summary['game_derived_aot_execution'] is False
 read=lambda name:json.loads((Path(folder)/name).read_text(encoding='utf-8'))
 audit=read('audit.json');data=read('input.json');inspection=read('inspection.json');assert audit['compiled_roots']==data['roots']==summary['compiled_roots'];assert not audit['unvisited_manifest_instructions'];assert audit['missing_instruction_starts']==summary['unreachable_missing_blocks'];contracts={r['address']:r for r in data['return_contracts']};assert len(contracts)==summary['nonreturn_contracts'];assert set(audit['missing_instruction_starts'])<={r['expected_next_pc'] for r in contracts.values()};assert summary['reachable_block_transfers']==0
 transfers=[s for s in inspection['sites'] if s['callee']=='__bb_native_block_transfer'];assert all(not s['cfg_reachable_from_entry'] and s['nounwind'] for s in transfers);assert {int(s['arguments'][4]['value_hex'],16) for s in transfers}==set(audit['missing_instruction_starts']);assert not {'__bb_native_block_transfer','__remill_error','__remill_missing_block'}&set(summary['undefined_symbols'])
 guards={(g['root'],g['source']):g for g in audit['call_return_checks']};assert {g['source'] for g in guards.values() if g['no_normal_return']}==set(contracts)
 for g in guards.values():
  if g['no_normal_return']:assert g['provenance']==contracts[g['source']]['provenance'] and g['expected_next_pc']==contracts[g['source']]['expected_next_pc']
 for site in inspection['sites']:
  if site['callee']!='__bb_native_control_fault':continue
  args=site['arguments'];assert site['nounwind'] and site['noreturn'];g=guards[site['function'],int(args[1]['value_hex'],16)];assert int(args[3]['value_hex'],16)==(2 if g['no_normal_return'] else 1) and int(args[4]['value_hex'],16)==g['expected_next_pc']
 ma=inspection['memory_source_audit'];assert not ma['invalid_sites'] and not ma['legacy_memory_calls'] and not inspection['indirect_llvm_calls']
