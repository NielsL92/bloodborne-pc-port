"""Malformed exception metadata must not invent reachable code."""
import struct
import unittest
from types import SimpleNamespace
from tools.formats import FormatError, checked_slice
from tools.exception_metadata import lsda_metadata, fde_metadata

class Memory:
    def __init__(self, payload, base=0x5000):
        self.payload=payload; self.base=base
        self.segments=[SimpleNamespace(vaddr=base,filesz=len(payload))]
    def at_va(self, address, size):
        return checked_slice(self.payload,address-self.base,size)

def parse(raw):
    return lsda_metadata(Memory(bytes.fromhex(raw)),dict(lsda=0x5000,start=0x1000,size=0x80))

class ExceptionMetadataTests(unittest.TestCase):
    def test_cleanup_and_signed_action_chain(self):
        # Omitted LPStart, no type table, uleb records: call [4,9) -> +32,
        # then [9,16) -> no local handler. Action filter -1, end of chain.
        result=parse("ff ff 01 08 04 05 20 01 09 07 00 00 7f 00")
        self.assertEqual(result["call_sites"][0]["landing_pad"],0x1020)
        self.assertIsNone(result["call_sites"][1]["landing_pad"])
        self.assertEqual(result["actions"],[dict(rva=0x500c,type_filter=-1,next_rva=None)])

    def test_action_cycle_rejected(self):
        with self.assertRaisesRegex(FormatError,"cyclic"):
            parse("ff ff 01 04 04 05 20 01 01 7f")

    def test_landing_outside_range_rejected(self):
        with self.assertRaisesRegex(FormatError,"landing pad"):
            parse("ff ff 01 05 04 05 80 01 00")

    def test_overlapping_intervals_rejected(self):
        with self.assertRaisesRegex(FormatError,"overlapping"):
            parse("ff ff 01 08 04 05 20 00 08 07 00 00")

    def test_call_record_cannot_consume_action_bytes(self):
        # Table declares three bytes but the action field lies outside it.
        with self.assertRaises(FormatError):
            parse("ff ff 01 03 04 05 20 00")

    def test_unsupported_encoding_rejected(self):
        with self.assertRaisesRegex(FormatError,"LPStart"):
            parse("30 ff 01 00")
        with self.assertRaisesRegex(FormatError,"call-site"):
            parse("ff ff 31 00")

    def test_fde_index_mismatch_rejected(self):
        cie=bytes.fromhex("1400000000000000017a5200017810011b0c070890010000")
        fde=struct.pack("<IIiI",16,28,0x1000-(0x5000+24+8),0x20)+bytes(4)
        memory=Memory(cie+fde)
        with self.assertRaisesRegex(FormatError,"disagreement"):
            fde_metadata(memory,dict(fde=0x5018,start=0x1001,size=0x20),{})

if __name__=="__main__":unittest.main()
