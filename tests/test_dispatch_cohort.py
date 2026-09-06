"""Reject branch/dataflow lookalikes in independent dispatch classification."""
import copy,unittest
from tools.check_dispatch_cohort import match_window,match_subobject_window

def fixture():
 texts=['LEA R12,[0x5540670]','MOV RBX,qword ptr [R12]','TEST RBX,RBX','JNZ 0x107','CALL 0x2ba2b10','MOV RBX,RAX','MOV qword ptr [R12],RBX','MOV RAX,qword ptr [RBX]','LEA RDI,[RSP + 0x8]','XOR EDX,EDX','MOV RSI,RBX','CALL qword ptr [RAX + 0x20]']
 rows=[dict(rva=0x100+n,length=1,text=t,flow='FALL_THROUGH',targets=[]) for n,t in enumerate(texts)]
 rows[3].update(flow='CONDITIONAL_JUMP',targets=[0x107]);rows[4].update(flow='UNCONDITIONAL_CALL',targets=[0x2ba2b10]);rows[11]['flow']='COMPUTED_CALL';return rows

def subobject_fixture(reload=False):
 rows=fixture();rows[0]['text']='LEA R12,[0x5540668]';rows[4]['targets']=[0x207bbf0];rows[4]['text']='CALL 0x207bbf0'
 rows.insert(6,dict(rva=0,length=1,text='ADD RBX,0x458',flow='FALL_THROUGH',targets=[]))
 if reload:
  for row in rows:row['text']=row['text'].replace('R12','RAX')
  rows.insert(7,dict(rva=0,length=1,text='LEA RAX,[0x5540668]',flow='FALL_THROUGH',targets=[]))
 for n,row in enumerate(rows):row['rva']=0x100+n
 rows[3]['targets']=[0x109 if reload else 0x108];return rows

class DispatchPatternTests(unittest.TestCase):
 def test_known_shape_and_initial_cache(self):
  r=match_window(fixture());self.assertEqual(r['cache_slot'],0x5540670);self.assertEqual(r['factory'],0x2ba2b10)
 def test_changed_branch_or_factory_stays_unknown(self):
  for index,targets in [(3,[0x108]),(4,[0x2ba2b20])]:
   rows=fixture();rows[index]['targets']=targets;self.assertIsNone(match_window(rows))
 def test_partial_segmented_and_indexed_loads_stay_unknown(self):
  for text in ['MOV EBX,dword ptr [R12]','MOV RBX,qword ptr FS:[R12]','MOV RBX,qword ptr [R12 + RAX*0x8]']:
   rows=fixture();rows[1]['text']=text;self.assertIsNone(match_window(rows))
 def test_wrong_object_or_result_register_stays_unknown(self):
  for index,text in [(5,'MOV RBX,RCX'),(6,'MOV qword ptr [R12],RAX'),(7,'MOV RAX,qword ptr [R13]'),(10,'MOV RSI,R12')]:
   rows=fixture();rows[index]['text']=text;self.assertIsNone(match_window(rows))
 def test_gap_or_incomplete_window_stays_unknown(self):
  rows=fixture();rows[4]['length']=2;self.assertIsNone(match_window(rows));self.assertIsNone(match_window(fixture()[:-1]))
 def test_different_slot_or_control_kind_stays_unknown(self):
  rows=fixture();rows[11]['text']='CALL qword ptr [RAX + 0x28]';self.assertIsNone(match_window(rows))
  rows=fixture();rows[3]['flow']='UNCONDITIONAL_JUMP';self.assertIsNone(match_window(rows))
class SubobjectPatternTests(unittest.TestCase):
 def test_both_exact_cache_forms(self):
  for reload in [False,True]:
   r=match_subobject_window(subobject_fixture(reload));self.assertEqual(r['object_offset'],0x458);self.assertEqual(r['cache_slot'],0x5540668)
 def test_wrong_adjustment_is_unknown(self):
  rows=subobject_fixture();rows[6]['text']='ADD RBX,0x450';self.assertIsNone(match_subobject_window(rows))
 def test_changed_reload_slot_is_unknown(self):
  rows=subobject_fixture(True);rows[7]['text']='LEA RAX,[0x5540670]';self.assertIsNone(match_subobject_window(rows))
 def test_volatile_cache_without_reload_is_unknown(self):
  rows=subobject_fixture()
  for row in rows:row['text']=row['text'].replace('R12','RAX')
  self.assertIsNone(match_subobject_window(rows))
 def test_branch_into_adjustment_is_unknown(self):
  rows=subobject_fixture();rows[3]['targets']=[rows[6]['rva']];self.assertIsNone(match_subobject_window(rows))
 def test_subobject_adjustment_does_not_match_whole_object(self):
  self.assertIsNone(match_window(subobject_fixture()));self.assertIsNone(match_subobject_window(fixture()))

if __name__=='__main__':unittest.main()
