"""Negative checks for service-site scope, evidence identity and retained runtime obligations."""
import copy,collections,unittest
from tools.cfg_service_sites import validate_site,match_site
from tools.startup_service_inventory import SPECS
from tests.test_startup_recovery import fixture

class ServiceSiteTests(unittest.TestCase):
 def setUp(self):
  self.row=copy.deepcopy(SPECS[0]);self.row['import_key']=[self.row['nid'],'libkernel','libkernel']
  self.row['instructions']=[[0x1f560,1,'55'],[0x1f561,3,'4889e5'],[0x1f564,5,'bf0b0002a0'],[0x1f569,2,'31f6'],[0x1f56b,5,'e8700bfeff'],[0x1f570,1,'90']]
  self.row['independent']={'call':dict(bytes='e8700bfeff',targets=[0xe0],flow='UNCONDITIONAL_CALL')}
  self.imp=dict(nid=self.row['nid'],library='libkernel',module='libkernel')
  self.memory={at:bytes.fromhex(raw) for at,_,raw in self.row['instructions']}
  class Image:
   def __init__(self,memory):self.memory=memory
   def at_va(self,at,size):return self.memory[at][:size]
  self.images={self.row['module']:Image(self.memory)}
 def validate(self,row=None,imp=None,pads=None):
  return validate_site(row or self.row,self.images,lambda h,at:imp or self.imp,pads or {})
 def test_original_exact_context_accepted(self):
  key,row=self.validate();self.assertEqual(key,(row['module'],row['entry'],row['site']))
 def test_modified_context_bytes_rejected(self):
  self.memory[0x1f569]=bytes.fromhex('31ff')
  with self.assertRaisesRegex(AssertionError,'bytes changed'):self.validate()
 def test_modified_policy_values_rejected(self):
  row=copy.deepcopy(self.row);row['context']['rsi']=1
  with self.assertRaises(AssertionError):self.validate(row)
 def test_new_landing_pad_rejected(self):
  with self.assertRaisesRegex(AssertionError,'entry path'):self.validate(pads={(self.row['module'],self.row['entry']):[self.row['site']]})
 def test_provider_and_library_collision_rejected(self):
  for key in ('nid','library','module'):
   with self.subTest(key=key):
    imp=dict(self.imp);imp[key]='other'
    with self.assertRaisesRegex(AssertionError,'binding changed'):self.validate(imp=imp)
 def test_generative_site_scope_does_not_expand(self):
  row=self.row;key=(row['module'],row['entry'],row['site']);sites={key:row}
  self.assertIs(match_site(sites,*key,row['target'],self.imp),row)
  for n in range(3):
   other=list(key);other[n]='other' if n==0 else other[n]+1
   self.assertIsNone(match_site(sites,*other,row['target'],self.imp))
 def test_mutated_target_or_binding_rejected_at_transfer(self):
  row=self.row;key=(row['module'],row['entry'],row['site']);sites={key:row}
  with self.assertRaises(AssertionError):match_site(sites,*key,row['target']+1,self.imp)
  with self.assertRaises(AssertionError):match_site(sites,*key,row['target'],dict(self.imp,nid='other'))
 def test_ghidra_wrong_target_rejected(self):
  self.row['independent']['call']['targets']=[0xf0]
  with self.assertRaises(AssertionError):self.validate()
 def test_recovery_retains_import_and_service_obligations(self):
  # Authored CALL 0x107; NOP; RET, with an exact fixture-only service annotation.
  r=fixture('e8 02 00 00 00 90 c3 c3');r.imported=lambda h,at:self.imp if at==0x107 else None
  row=dict(self.row,target=0x107);r.service_sites={('test',0x100,0x100):row}
  r.recover('test',0x100)
  kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
  self.assertIn('import_contract_unvalidated',kinds);self.assertIn('unresolved_native_service_control',kinds)
  self.assertIn('annotated_control_contract_requires_runtime',kinds)
  self.assertNotIn('fallthrough',kinds)
  self.assertEqual(r.db.execute('SELECT count(*) FROM recovery_instruction').fetchone()[0],1)
 def test_unannotated_debug_call_preserves_return(self):
  r=fixture('e8 02 00 00 00 90 c3 c3');r.imported=lambda h,at:self.imp if at==0x107 else None
  r.recover('test',0x100)
  kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
  self.assertIn('fallthrough',kinds);self.assertNotIn('annotated_control_contract_requires_runtime',kinds)
  self.assertEqual(r.db.execute('SELECT count(*) FROM recovery_instruction').fetchone()[0],3)
if __name__=='__main__':unittest.main()
