"""Adversarial role, binding, byte and unknown-target checks for symbol dispatch."""
import copy,unittest
from tools.cfg_symbol_dispatch import validate_candidate
from tests.test_startup_recovery import fixture

class SymbolDispatchTests(unittest.TestCase):
 def setUp(self):
  self.symbols=[dict(index=0,name='table#A#A',nid='table',library='libc',module='libc',defined=True,type=1,value=0x200,size=48),dict(index=1,name='method#A#A',nid='method',library='libc',module='libc',defined=True,type=2,value=0x300,size=1)]
  self.rel=[dict(offset=0x100,type=1,symbol=0,addend=16,table='rela'),dict(offset=0x220,type=1,symbol=1,addend=0,table='rela')]
  self.row=dict(module='m',module_sha256='m',owner=0x1000,site=0x1000,object_slot=0x100,table_offset=0x10,target=0x300,source_instructions=[dict(rva=0x1000,size=2,bytes='ffd0')],target_body=[dict(rva=0x300,size=1,bytes='c3')],chain=[dict(slot=x['offset'],raw_word='00'*8,relocation=copy.deepcopy(x),symbol=copy.deepcopy(self.symbols[n]),initial_target=self.symbols[n]['value']+x['addend']) for n,x in enumerate(self.rel)])
  self.mem={0x100:bytes(8),0x220:bytes(8),0x1000:bytes.fromhex('ffd0'),0x300:bytes.fromhex('c3')}
  class Image:
   def __init__(self,m):self.m=m
   def at_va(self,a,n):return self.m[a][:n]
  self.images={'m':Image(self.mem)};self.links={'m':dict(symbols=self.symbols)};self.relocs={'m':{r['offset']:r for r in self.rel}}
 def validate(self):return validate_candidate(self.row,self.images,self.links,self.relocs,lambda h,a:a==0x300)
 def test_valid_initial_chain(self):self.assertEqual(self.validate()[0],('m',0x1000,0x1000))
 def test_relocation_addend_change_rejected(self):
  self.relocs['m'][0x100]['addend']=24
  with self.assertRaisesRegex(AssertionError,'relocation changed'):self.validate()
 def test_wrong_symbol_role_rejected(self):
  self.symbols[1]['type']=1
  with self.assertRaisesRegex(AssertionError,'definition changed'):self.validate()
 def test_undefined_symbol_rejected(self):
  self.symbols[0]['defined']=False
  with self.assertRaisesRegex(AssertionError,'definition changed'):self.validate()
 def test_duplicate_provider_definition_rejected(self):
  self.links['other']=dict(symbols=copy.deepcopy(self.symbols))
  with self.assertRaisesRegex(AssertionError,'ambiguous'):self.validate()
 def test_changed_table_cell_rejected(self):
  self.mem[0x220]=bytes.fromhex('0100000000000000')
  with self.assertRaisesRegex(AssertionError,'table cell changed'):self.validate()
 def test_changed_target_code_rejected(self):
  self.mem[0x300]=bytes.fromhex('90')
  with self.assertRaisesRegex(AssertionError,'witness bytes changed'):self.validate()
 def test_wrong_table_offset_rejected(self):
  self.row['table_offset']=24
  with self.assertRaises(AssertionError):self.validate()
 def test_wrong_owner_or_site_rejected(self):
  for key in ('owner','site'):
   row=copy.deepcopy(self.row);self.row[key]+=1
   with self.assertRaises(AssertionError):self.validate()
   self.row=row
 def test_recovery_adds_candidate_and_keeps_unknown(self):
  r=fixture('ff d0 c3 90 c3');r.symbol_dispatch={('test',0x100,0x100):[dict(object_slot=0x200,table_offset=16,target=0x104)]};r.symbol_dispatch_evidence_sha256='authored-fixture'
  r.recover('test',0x100)
  kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
  self.assertIn('unresolved_indirect_call',kinds);self.assertIn('symbol_dispatch_binding_unvalidated',kinds);self.assertIn('initial_symbol_dispatch_target_candidate',kinds)
  self.assertIn('fallthrough',kinds);self.assertIn(('test',0x104),r.queue)
 def test_other_entry_does_not_gain_candidate(self):
  r=fixture('ff d0 c3 90 c3');r.symbol_dispatch={('test',0x101,0x100):[dict(object_slot=0x200,table_offset=16,target=0x104)]};r.symbol_dispatch_evidence_sha256='authored-fixture';r.recover('test',0x100)
  self.assertNotIn(('test',0x104),r.queue)
  self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_indirect_call'").fetchone()[0],1)
if __name__=='__main__':unittest.main()
