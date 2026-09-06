import collections,unittest
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM
from tools.cfg_callback_slices import slice_register

def probe(raw,query='rdi',extra_roots=(),budget=2048):
 d=Cs(CS_ARCH_X86,CS_MODE_64);d.detail=True;ins={i.address:i for i in d.disasm(bytes.fromhex(raw),0x100)};pred=collections.defaultdict(set)
 for pc,i in ins.items():
  if i.group(CS_GRP_JUMP) and i.operands[0].type==X86_OP_IMM:pred[i.operands[0].imm].add(pc)
  if not i.group(CS_GRP_RET) and i.mnemonic!='jmp' and pc+i.size in ins:pred[pc+i.size].add(pc)
 return slice_register(ins,pred,{0x100,*extra_roots},max(ins),query,budget)

class CallbackSliceTests(unittest.TestCase):
 def test_same_constant_both_branch_arms(self):
  r=probe('74 07 bf 44 00 00 00 eb 05 bf 44 00 00 00 c3');self.assertTrue(r['complete']);self.assertEqual(r['targets'],[dict(kind='absolute',value=0x44)])
 def test_distinct_arms_remain_a_target_set(self):
  r=probe('74 07 bf 44 00 00 00 eb 05 bf 55 00 00 00 c3');self.assertTrue(r['complete']);self.assertEqual(len(r['targets']),2)
 def test_unknown_arm_is_not_closed_by_known_arm(self):
  r=probe('74 05 bf 44 00 00 00 c3');self.assertFalse(r['complete']);self.assertEqual(r['failures'][0]['reason'],'entry-register')
 def test_reconverging_branches_reuse_completed_states(self):
  r=probe('bb 44 00 00 00 '+('74 01 90 '*28)+'48 89 df c3');self.assertTrue(r['complete']);self.assertEqual(r['targets'],[dict(kind='absolute',value=0x44)]);self.assertLess(r['states'],100)
 def test_deep_slice_uses_bounded_worklist(self):
  r=probe('bb 44 00 00 00 '+('90 '*1600)+'48 89 df c3',budget=2000);self.assertTrue(r['complete']);self.assertEqual(r['targets'],[dict(kind='absolute',value=0x44)]);self.assertLess(r['states'],2000)
 def test_partial_write_blocks_slice(self):
  r=probe('bf 44 00 00 00 40 b7 00 c3');self.assertFalse(r['complete'])
 def test_loop_and_budget_are_unknown(self):
  r=probe('bf 44 00 00 00 90 75 fd c3');self.assertFalse(r['complete']);self.assertIn('cycle',{x['reason'] for x in r['failures']});self.assertFalse(probe('bf 44 00 00 00 90 c3',budget=1)['complete'])
 def test_additional_entry_root_is_unknown(self):
  self.assertFalse(probe('bf 44 00 00 00 90 c3',extra_roots=(0x105,))['complete'])
 def test_calls_clobber_volatile_but_preserve_conditionally(self):
  self.assertFalse(probe('bf 44 00 00 00 e8 00 00 00 00 c3')['complete'])
  r=probe('bb 44 00 00 00 e8 00 00 00 00 48 89 df c3');self.assertTrue(r['complete']);self.assertEqual(r['conditional_normal_sysv_returns'],[0x105])
 def test_module_relative_address_is_not_literal_null(self):
  r=probe('48 8d 3d f9 fe ff ff c3');self.assertTrue(r['complete']);self.assertEqual(r['targets'],[dict(kind='module-rva',value=0)])
if __name__=='__main__':unittest.main()
