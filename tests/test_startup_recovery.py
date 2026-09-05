"""Adversarial decode and candidate-provenance checks, without game execution."""
import collections
import sqlite3
import unittest
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import Recovery

class BytesImage:
    def __init__(self, raw): self.raw=bytes.fromhex(raw)
    def at_va(self, address, size): return self.raw[address-0x100:address-0x100+size]

def fixture(raw):
    r=Recovery.__new__(Recovery)
    r.decoder=Cs(CS_ARCH_X86,CS_MODE_64);r.decoder.detail=True
    im=BytesImage(raw);r.images={'test':im};end=0x100+len(im.raw)
    r.executable={'test':[(0x100,end)]};r.ranges={'test':([0x100],{0x100:len(im.raw)})}
    r.fences={'test':[0x100]};r.code_seeds={'test':{0x100}};r.max_instructions=100;r.main='test'
    r.byte_owners=collections.defaultdict(dict);r.pads={};r.regions={}
    r.known=collections.defaultdict(list);r.relocs={'test':{}};r.local_contracts={}
    r.static_tables=set();r.import_cache={};r.contracts={};r.exports={};r.queue=collections.deque();r.requested=set()
    r.db=sqlite3.connect(':memory:')
    r.db.executescript('''
    CREATE TABLE recovery_instruction(module,rva,size,bytes,mnemonic,operands,PRIMARY KEY(module,rva));
    CREATE TABLE recovery_owner(module,entry,rva);
    CREATE TABLE recovery_edge(module,entry,source,target_module,target,kind,detail);
    CREATE TABLE recovery_issue(module,entry,rva,kind,detail);
    CREATE TABLE recovery_reference(module,entry,source,target,operation,write_access);
    CREATE TABLE recovery_entry(module,start,fence,fence_reason,status,instructions,issues);
    CREATE TABLE recovery_request(module,target,reason,parent_module,parent_entry,source);
    ''')
    return r

class RecoveryTests(unittest.TestCase):
    def test_return_leaves_embedded_data_undecoded(self):
        r=fixture('c3 0f ff ff ff');r.recover('test',0x100)
        self.assertEqual(r.db.execute('SELECT rva FROM recovery_instruction').fetchall(),[(0x100,)])
        self.assertEqual(r.db.execute('SELECT count(*) FROM recovery_issue').fetchone()[0],0)

    def test_fallthrough_does_not_silently_cross_fence(self):
        r=fixture('90 90 c3');r.ranges={'test':([0x100],{0x100:1})};r.recover('test',0x100)
        self.assertEqual(r.db.execute('SELECT kind FROM recovery_issue').fetchall(),[('fallthrough_at_fence',)])
        self.assertEqual(len(r.queue),0)

    def test_branch_into_instruction_is_quarantined(self):
        r=fixture('75 01 b8 01 00 00 00 c3');r.recover('test',0x100)
        self.assertTrue({'overlapping_decode_target','overlapping_decode_bytes'} & {x[0] for x in r.db.execute('SELECT kind FROM recovery_issue')})

    def test_unknown_indirect_is_retained_with_constant_candidate(self):
        r=fixture('48 8d 05 03 00 00 00 ff d0 c3 c3');r.recover('test',0x100)
        kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
        self.assertIn('unresolved_indirect_call',kinds)
        self.assertIn('indirect_target_candidate',kinds)
        self.assertEqual(len(r.queue),0)  # Executable-pointer candidate is not a proven code seed.

    def test_partial_register_write_invalidates_candidate(self):
        r=fixture('48 8d 05 05 00 00 00 b0 00 ff d0 c3 c3');r.recover('test',0x100)
        kinds=[x[0] for x in r.db.execute('SELECT kind FROM recovery_edge')]
        self.assertIn('unresolved_indirect_call',kinds)
        self.assertNotIn('indirect_target_candidate',kinds)

    def test_branch_merge_does_not_invent_callback(self):
        r=fixture('48 8d 3d 09 00 00 00 75 00 e8 02 00 00 00 c3 90 c3');r.recover('test',0x100)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='callback_argument_candidate'").fetchone()[0],0)

    def test_seeded_constant_indirect_is_expanded_but_still_unvalidated(self):
        r=fixture('48 8d 05 03 00 00 00 ff d0 c3 c3')
        r.code_seeds['test'].add(0x10a);r.recover('test',0x100)
        self.assertIn(('test',0x10a),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_indirect_call'").fetchone()[0],1)

    def test_exception_pad_is_decoded_without_intervening_padding(self):
        r=fixture('c3 90 90 b8 01 00 00 00 c3')
        r.pads['test',0x100]=[0x103];r.recover('test',0x100)
        self.assertEqual(r.db.execute('SELECT rva FROM recovery_instruction ORDER BY rva').fetchall(),[(0x100,),(0x103,),(0x108,)])

    def test_explicit_jump_crosses_fence_as_separate_request(self):
        r=fixture('e9 02 00 00 00 90 90 c3')
        r.ranges={'test':([0x100],{0x100:5})};r.recover('test',0x100)
        self.assertIn(('test',0x107),r.queue)
        self.assertEqual(r.db.execute('SELECT count(*) FROM recovery_instruction').fetchone()[0],1)

if __name__=='__main__':unittest.main()
