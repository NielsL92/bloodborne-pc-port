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
    r.callback_contracts={};r.local_callback_contracts={}
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
    def callback_fixture(self, raw, target):
        r=fixture(raw)
        r.local_callback_contracts['test',target]=dict(id='test-registration',register='rdi',nullable=False,callback_signature='void(void*)',context_registers=[])
        return r

    def test_callback_abi_expands_unindexed_entry(self):
        r=self.callback_fixture('48 8d 3d 07 00 00 00 e8 01 00 00 00 c3 c3 c3',0x10d)
        r.recover('test',0x100)
        self.assertIn(('test',0x10e),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='callback_contract_target_candidate'").fetchone()[0],1)

    def test_tail_registration_captures_callback(self):
        r=self.callback_fixture('48 8d 3d 07 00 00 00 e9 01 00 00 00 c3 c3 c3',0x10d)
        r.recover('test',0x100)
        self.assertIn(('test',0x10e),r.queue)

    def test_unknown_registration_argument_is_retained(self):
        r=self.callback_fixture('e8 01 00 00 00 c3 c3',0x106);r.recover('test',0x100)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchone()[0],1)

    def test_full_zero_idiom_resolves_nullable_callback(self):
        for raw in ('31 ff', '48 31 ff', '29 ff', '48 29 ff'):
            with self.subTest(raw=raw):
                prefix=bytes.fromhex(raw);target=0x100+len(prefix)+6
                r=self.callback_fixture(raw+' e8 01 00 00 00 c3 c3',target)
                r.local_callback_contracts['test',target]['nullable']=True
                r.executable['test']=[(0,r.executable['test'][0][1])]  # RVA zero lies in a code mapping but null is not an entry.
                r.recover('test',0x100)
                rows=r.db.execute("SELECT kind,detail FROM recovery_edge WHERE kind LIKE '%callback%'").fetchall()
                self.assertEqual([x[0] for x in rows],['callback_contract_null_argument'])
                self.assertEqual(__import__('json').loads(rows[0][1])['provenance'],[0x100])

    def test_partial_zero_idiom_does_not_invent_null(self):
        for raw in ('66 31 ff','40 30 ff'):
            with self.subTest(raw=raw):
                target=0x100+len(bytes.fromhex(raw))+6
                r=self.callback_fixture(raw+' e8 01 00 00 00 c3 c3',target)
                r.local_callback_contracts['test',target]['nullable']=True
                r.executable['test']=[(0,r.executable['test'][0][1])]  # RVA zero lies in a code mapping but null is not an entry.
                r.recover('test',0x100)
                self.assertEqual(r.db.execute("SELECT kind FROM recovery_edge WHERE kind LIKE '%callback%'").fetchall(),[('unresolved_callback_argument',)])

    def test_zero_nonnullable_callback_remains_unresolved(self):
        r=self.callback_fixture('31 ff e8 01 00 00 00 c3 c3',0x108);r.recover('test',0x100)
        self.assertEqual(r.db.execute("SELECT target,kind FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchall(),[(0,'unresolved_callback_argument')])

    def test_rip_relative_rva_zero_is_not_literal_null(self):
        r=self.callback_fixture('48 8d 3d f9 fe ff ff e8 01 00 00 00 c3 c3',0x10d)
        r.executable['test']=[(0,0x10e)];r.local_callback_contracts['test',0x10d]['nullable']=True
        r.recover('test',0x100)
        self.assertEqual(r.db.execute("SELECT target,kind FROM recovery_edge WHERE kind LIKE '%callback%'").fetchall(),[(0,'unresolved_callback_argument')])

    def test_other_register_xor_remains_unknown(self):
        r=self.callback_fixture('31 f7 e8 01 00 00 00 c3 c3',0x108);r.recover('test',0x100)
        self.assertEqual(r.db.execute("SELECT target,kind FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchall(),[(None,'unresolved_callback_argument')])

    def across_call_fixture(self, clobber=b'', reg='rbx', enabled=True):
        import struct
        # LEA register, callback; call helper; optional clobber; move into RDI;
        # call registrar; RET; then three independent RET bodies.
        prefix=bytes.fromhex('48 8d 1d' if reg=='rbx' else '48 8d 05')
        move=bytes.fromhex('48 89 df' if reg=='rbx' else '48 89 c7')
        callback=0x100+7+5+len(clobber)+3+5+1
        helper,registrar=callback+1,callback+2
        raw=prefix+struct.pack('<i',callback-0x107)+b'\xe8'+struct.pack('<i',helper-0x10c)+clobber+move
        raw+=b'\xe8'+struct.pack('<i',registrar-(0x100+len(raw)+5))+b'\xc3'*4
        r=self.callback_fixture(raw.hex(),registrar);r.sysv_callee_saved_candidates=enabled
        r.recover('test',0x100)
        return r,callback

    def test_conditional_callee_saved_constant_survives_call(self):
        r,target=self.across_call_fixture()
        self.assertIn(('test',target),r.queue)
        rows=r.db.execute("SELECT kind,detail FROM recovery_edge WHERE kind='abi_register_preservation_unvalidated'").fetchall()
        self.assertTrue(rows)
        provenance=__import__('json').loads(rows[0][1])['registers']['rbx'][1]
        self.assertEqual(provenance,[0x100,0x107])

    def test_callee_saved_candidate_mode_is_explicit(self):
        r,target=self.across_call_fixture(enabled=False)
        self.assertNotIn(('test',target),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchone()[0],1)

    def test_volatile_constant_does_not_survive_call(self):
        r,target=self.across_call_fixture(reg='rax')
        self.assertNotIn(('test',target),r.queue)

    def test_partial_callee_saved_write_invalidates_constant(self):
        r,target=self.across_call_fixture(bytes.fromhex('b3 00'))
        self.assertNotIn(('test',target),r.queue)

    def test_branch_still_invalidates_callee_saved_constant(self):
        r,target=self.across_call_fixture(bytes.fromhex('75 00'))
        self.assertNotIn(('test',target),r.queue)

    def relocated_callback_fixture(self, width=8, clobber=b'', segment=False):
        import struct
        load=bytes.fromhex('48 8b 3d') if width==8 else bytes.fromhex('8b 3d')
        if segment:load=b'\x64'+load
        instruction_size=len(load)+4;callback=0x100+instruction_size+len(clobber)+5+1;slot=callback+1;registrar=slot+8
        raw=load+struct.pack('<i',slot-(0x100+instruction_size))+clobber
        raw+=b'\xe8'+struct.pack('<i',registrar-(0x100+len(raw)+5))+b'\xc3\xc3'+b'\0'*8+b'\xc3'
        r=self.callback_fixture(raw.hex(),registrar);r.initial_callback_relocation_candidates=True
        r.relocs['test'][slot]=dict(offset=slot,type=8,addend=callback,symbol=0)
        return r,callback,slot

    def test_initial_relative_callback_slot_expands_but_stays_unknown(self):
        r,target,slot=self.relocated_callback_fixture();r.recover('test',0x100)
        self.assertIn(('test',target),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchone()[0],1)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='callback_relocation_binding_unvalidated'").fetchone()[0],1)

    def test_truncated_or_clobbered_callback_slot_is_not_promoted(self):
        for width,clobber in [(4,b''),(8,bytes.fromhex('40 b7 00')),(8,bytes.fromhex('75 00'))]:
            with self.subTest(width=width,clobber=clobber):
                r,target,slot=self.relocated_callback_fixture(width,clobber);r.recover('test',0x100)
                self.assertNotIn(('test',target),r.queue)

    def test_segment_based_callback_load_is_not_module_relocation(self):
        r,target,slot=self.relocated_callback_fixture(segment=True);r.recover('test',0x100)
        self.assertNotIn(('test',target),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='callback_relocation_binding_unvalidated'").fetchone()[0],0)

    def test_symbolic_callback_slot_requires_exact_function_provider(self):
        r,target,slot=self.relocated_callback_fixture()
        symbol=dict(type=2,defined=False,value=0,nid='test',library='library',module='provider')
        r.links={'test':{'symbols':[symbol]}};r.relocs['test'][slot].update(type=6,addend=0)
        r.exports={('test','library','provider'):[('test',target)]}
        self.assertEqual(r.initial_function_slot('test',slot)['candidates'],[dict(module='test',target=target)])
        r.exports[('test','library','provider')].append(('test',target+1))
        self.assertEqual(r.initial_function_slot('test',slot)['candidates'],[])
        r.exports[('test','library','provider')].pop();symbol['type']=1
        self.assertEqual(r.initial_function_slot('test',slot)['candidates'],[])
        symbol['type']=2;r.relocs['test'][slot]['addend']=1
        self.assertEqual(r.initial_function_slot('test',slot)['candidates'],[])

    def test_checked_callback_slice_seeds_target_with_runtime_obligation(self):
        r=self.callback_fixture('e8 01 00 00 00 c3 c3 c3',0x106)
        r.callback_slices={('test',0x100,0x100):dict(targets=[dict(kind='module-rva',value=0x107)],conditional_normal_sysv_returns=[])}
        r.callback_slice_evidence_sha256='fixture checked proof';r.recover('test',0x100)
        self.assertIn(('test',0x107),r.queue)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='callback_slice_runtime_unvalidated'").fetchone()[0],1)
        self.assertEqual(r.db.execute("SELECT count(*) FROM recovery_edge WHERE kind='unresolved_callback_argument'").fetchone()[0],0)

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
