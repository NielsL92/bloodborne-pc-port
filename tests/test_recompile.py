import unittest

from tools.recompile import Unsupported, lift


class RecompileTests(unittest.TestCase):
    def test_arithmetic_leaf_is_accepted(self):
        # Synthetic: mov eax,edi; add eax,esi; imul eax,eax,7; ret.
        _, operations, _ = lift(bytes.fromhex('89f801f06bc007c3'), 0)
        self.assertEqual(operations, 2)

    def test_memory_load_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('488b07c3'), 0)

    def test_memory_store_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('488937c3'), 0)

    def test_stack_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('555dc3'), 0)

    def test_call_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('e800000000c3'), 0)

    def test_branch_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('740089f8c3'), 0)

    def test_incoming_flags_are_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('89f80f94c0c3'), 0)

    def test_uninitialized_full_register_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('01f8c3'), 0)

    def test_uninitialized_upper_return_bits_are_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('b001c3'), 0)

    def test_zero_idiom_defines_full_register(self):
        lift(bytes.fromhex('31c0b001c3'), 0)

    def test_rip_relative_lea_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('488d0500000000c3'), 0)

    def test_extra_bytes_after_ret_are_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('89f8c3c3'), 0)

    def test_partial_instruction_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('89f8c3e8'), 0)

    def test_host_nonvolatile_register_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('4889fb4889d8c3'), 0)

    def test_sse_is_rejected(self):
        with self.assertRaises(Unsupported):
            lift(bytes.fromhex('660fefc031c0c3'), 0)


if __name__ == '__main__':
    unittest.main()
