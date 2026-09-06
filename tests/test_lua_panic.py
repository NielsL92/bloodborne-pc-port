"""Authored negative checks for mutable callback fields and scoped recovery expansion."""
import copy,struct,unittest
from tools.cfg_lua_panic import validate_candidate
from tests.test_startup_recovery import fixture
class LuaPanicTests(unittest.TestCase):
 def setUp(self):
  def ins(pc,b):return dict(rva=pc,size=len(bytes.fromhex(b)),bytes=b)
  call=[ins(0x100,'488b4720'),ins(0x104,'ff5050')]
  assign=[ins(0x200,'488d0d'+struct.pack('<i',0x300-0x207).hex()),ins(0x207,'48894850')]
  target=[ins(0x300,'c3')]
  self.row=dict(module='m',module_sha256='m',global_offset=32,field_offset=80,conditions=['same mutable global object'],limitations=['no execution'],owner=0x100,site=0x104,global_load=0x100,owners=[dict(entry=0x100,instructions=call),dict(entry=0x200,instructions=assign)],assignments=[dict(entry=0x200,lea=0x200,store=0x207,target=0x300,role='authored callback',body=target)])
  self.mem={i['rva']:bytes.fromhex(i['bytes']) for i in call+assign+target}
  class Image:
   def __init__(self,m):self.m=m
   def at_va(self,a,n):return self.m[a][:n]
  self.images={'m':Image(self.mem)}
 def validate(self):return validate_candidate(self.row,self.images,lambda h,pc:pc==0x300)
 def test_valid_conditional_store(self):self.assertEqual(self.validate()[0],('m',0x100,0x104))
 def test_changed_witness_rejected(self):
  self.mem[0x207]=bytes.fromhex('48894858')
  with self.assertRaisesRegex(AssertionError,'witness bytes changed'):self.validate()
 def test_wrong_field_role_rejected(self):
  self.row['field_offset']=64
  with self.assertRaisesRegex(AssertionError,'field layout'):self.validate()
 def test_wrong_call_operands_rejected(self):
  self.row['owners'][0]['instructions'][1]['bytes']='ff5058';self.mem[0x104]=bytes.fromhex('ff5058')
  with self.assertRaisesRegex(AssertionError,'dispatch operands'):self.validate()
 def test_wrong_store_base_rejected(self):
  self.row['owners'][1]['instructions'][1]['bytes']='48894950';self.mem[0x207]=bytes.fromhex('48894950')
  with self.assertRaisesRegex(AssertionError,'callback store'):self.validate()
 def test_mismatched_target_rejected(self):
  self.row['assignments'][0]['target']+=1
  with self.assertRaisesRegex(AssertionError,'target mismatch'):self.validate()
 def test_changed_body_rejected(self):
  self.mem[0x300]=bytes.fromhex('90')
  with self.assertRaisesRegex(AssertionError,'target bytes changed'):self.validate()
 def test_missing_conditions_rejected(self):
  self.row['conditions']=[]
  with self.assertRaisesRegex(AssertionError,'conditional evidence'):self.validate()
 def test_wrong_owner_rejected(self):
  self.row['owner']=0x101
  with self.assertRaises(AssertionError):self.validate()
 def test_unknown_call_and_fallthrough_retained(self):
  r=fixture('ff d0 c3 90 c3');r.lua_panic={('test',0x100,0x100):[dict(target=0x104,assignment_entry=0x200,assignment_site=0x207,role='fixture',conditions=['same object'])]};r.lua_panic_evidence_sha256='fixture';r.recover('test',0x100)
  kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
  for kind in ('unresolved_indirect_call','fallthrough','lua_panic_binding_unvalidated','stored_lua_panic_target_candidate'):self.assertIn(kind,kinds)
  self.assertIn(('test',0x104),r.queue)
 def test_other_owner_keeps_unknown_without_candidate(self):
  r=fixture('ff d0 c3 90 c3');r.lua_panic={('test',0x101,0x100):[dict(target=0x104)]};r.recover('test',0x100)
  self.assertNotIn(('test',0x104),r.queue)
  self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_indirect_call'").fetchone()[0],1)
if __name__=='__main__':unittest.main()
