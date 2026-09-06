"""Adversarial authored flow checks; callbacks never become terminal or resolved."""
import copy,unittest
from tools.cfg_conditional_control import independent_paths,match_site
from tests.test_startup_recovery import fixture
class ConditionalControlTests(unittest.TestCase):
 def setUp(self):
  self.ins=[dict(rva=0x100,length=2,bytes='ffd0',flow='COMPUTED_CALL',targets=[]),dict(rva=0x102,length=5,bytes='e800000000',flow='UNCONDITIONAL_CALL',targets=[0x200])]
 def test_explicit_ordinary_call_condition(self):self.assertEqual(independent_paths(self.ins,[0x100],{0x102},{0x100:'ffd0'}),[0x100,0x102])
 def test_unknown_callback_without_condition_rejects(self):self.assertIsNone(independent_paths(self.ins,[0x100],{0x102},{}))
 def test_computed_jump_is_not_ordinary_call(self):
  self.ins[0]['flow']='COMPUTED_JUMP'
  with self.assertRaisesRegex(AssertionError,'callback form'):independent_paths(self.ins,[0x100],{0x102},{0x100:'ffd0'})
 def test_changed_instruction_rejects(self):
  self.ins[0]['bytes']='ffd1'
  with self.assertRaisesRegex(AssertionError,'callback form'):independent_paths(self.ins,[0x100],{0x102},{0x100:'ffd0'})
 def test_callback_cannot_be_terminal(self):
  with self.assertRaisesRegex(AssertionError,'terminal form'):independent_paths(self.ins,[0x100],{0x100},{0x100:'ffd0'})
 def test_return_bypasses_terminal_rejects(self):
  self.ins[0]['flow']='TERMINATOR';self.assertIsNone(independent_paths(self.ins,[0x100],{0x102},{}))
 def test_missing_fallthrough_rejects(self):
  self.ins[0]['length']=3;self.assertIsNone(independent_paths(self.ins,[0x100],{0x102},{0x100:'ffd0'}))
 def test_cycle_rejects(self):
  self.ins[0].update(flow='UNCONDITIONAL_JUMP',targets=[0x100]);self.assertIsNone(independent_paths(self.ins,[0x100],{0x102},{}))
 def test_additional_unknown_root_rejects(self):self.assertIsNone(independent_paths(self.ins,[0x100,0x999],{0x102},{0x100:'ffd0'}))
 def test_unused_callback_condition_rejects(self):
  with self.assertRaisesRegex(AssertionError,'unvisited callback'):independent_paths(self.ins,[0x102],{0x102},{0x100:'ffd0'})
 def test_exact_site_scope_and_target(self):
  sites={('m',0x10,0x20):dict(target=0x30)};self.assertIsNone(match_site(sites,'m',0x11,0x20,0x30))
  with self.assertRaisesRegex(AssertionError,'target changed'):match_site(sites,'m',0x10,0x20,0x31)
 def test_recovery_keeps_runtime_obligation(self):
  r=fixture('e8 03 00 00 00 90 90 90 c3');r.conditional_control_sites={('test',0x100,0x100):dict(target=0x108,id='authored',proof_id='proof',conditions=['ordinary callback ABI'])};r.recover('test',0x100)
  kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
  self.assertIn('unresolved_conditional_control_continuation',kinds);self.assertIn('annotated_control_contract_requires_runtime',kinds);self.assertNotIn('fallthrough',kinds);self.assertIn(('test',0x108),r.queue)
if __name__=='__main__':unittest.main()
