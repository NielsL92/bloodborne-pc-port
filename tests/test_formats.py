import struct
import tempfile
from pathlib import Path
import unittest

from tools.formats import ElfImage, FormatError, checked_slice, inspect_pkg, read_sfo


def elf(payload=b'\xc3', *, flags=5, memsize=None):
    header = struct.pack('<16sHHIQQQIHHHHHH', b'\x7fELF\2\1\1' + b'\0' * 9,
                         0xFE10, 62, 1, 0, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    ph = struct.pack('<II6Q', 1, flags, 0x100, 0, 0, len(payload),
                     len(payload) if memsize is None else memsize, 0x100)
    return header + ph + bytes(0x100 - len(header) - len(ph)) + payload


def self_image(segment_flags=0x800):
    raw = elf(b'\x89\xf8\xc3')  # Synthetic identity function, not game code.
    header = bytearray(32)
    header[:10] = b'\x4f\x15\x3d\x1d\0\1\1\x12\1\1'
    struct.pack_into('<H', header, 24, 1)
    segment = struct.pack('<4Q', segment_flags, 0x200, 3, 3)
    data = header + segment + raw[:120]
    return bytes(data + bytes(0x200 - len(data)) + raw[0x100:])


class FormatTests(unittest.TestCase):
    def test_read_real_elf_layout_and_bss(self):
        image = ElfImage(elf(b'ABC', memsize=8192))
        self.assertEqual(image.at_va(1, 2), b'BC')
        with self.assertRaises(FormatError):
            image.at_va(3, 1)  # BSS has no file bytes.

    def test_self_uses_segment_mapping(self):
        image = ElfImage(self_image())
        self.assertEqual(image.at_va(0, 3), b'\x89\xf8\xc3')
        raw, missing = image.unwrap()
        self.assertEqual(missing, [])
        self.assertEqual(ElfImage(raw).at_va(0, 3), image.at_va(0, 3))

    def test_encrypted_program_is_rejected(self):
        with self.assertRaisesRegex(FormatError, 'Encrypted'):
            ElfImage(self_image(0x802))

    def test_compressed_program_is_rejected(self):
        with self.assertRaisesRegex(FormatError, 'compressed'):
            ElfImage(self_image(0x808))

    def test_invalid_self_program_index_is_rejected(self):
        with self.assertRaisesRegex(FormatError, 'invalid program header'):
            ElfImage(self_image(0x100800))

    def test_truncation_is_rejected(self):
        for size in [0, 3, 16, 63, 64, 119, 256]:
            with self.subTest(size=size), self.assertRaises(FormatError):
                ElfImage(elf()[:size])

    def test_wrong_architecture_is_rejected(self):
        raw = bytearray(elf())
        struct.pack_into('<H', raw, 18, 183)
        with self.assertRaises(FormatError):
            ElfImage(bytes(raw))

    def test_impossible_load_size_is_rejected(self):
        with self.assertRaises(FormatError):
            ElfImage(elf(b'ABC', memsize=2))

    def test_out_of_bounds_reads(self):
        for offset, size in [(-1, 1), (0, -1), (2, 2), (4, 0)]:
            with self.subTest(offset=offset, size=size), self.assertRaises(FormatError):
                checked_slice(b'abc', offset, size)

    def test_sfo_utf8(self):
        payload = b'01.09\0'
        data = struct.pack('<5I', 0x46535000, 0x101, 36, 44, 1)
        data += struct.pack('<HHIII', 0, 0x204, 6, 8, 0)
        data += b'APP_VER\0' + payload + b'\0\0'
        self.assertEqual(read_sfo(data), {'APP_VER': '01.09'})
        bad = bytearray(data)
        struct.pack_into('<I', bad, 24, 9)
        with self.assertRaises(FormatError):
            read_sfo(bytes(bad))

    def test_corrupt_pkg_table_is_rejected_before_large_read(self):
        data = bytearray(256)
        data[:4] = b'\x7fCNT'
        struct.pack_into('>I', data, 16, 0xFFFFFFFF)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.pkg'
            path.write_bytes(data)
            with self.assertRaises(FormatError):
                inspect_pkg(path)


if __name__ == '__main__':
    unittest.main()
