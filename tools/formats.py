"""Bounded readers for local PS4 PKG metadata and decrypted SELF/ELF images.

SPDX-License-Identifier: GPL-2.0-or-later
Format reference: shadPS4 src/core/loader/elf.h and src/core/module.cpp;
LibOrbisPkg LibOrbisPkg/PKG/Entry.cs. See THIRD_PARTY.md.
No cryptographic keys or executable decryption are implemented here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import struct


class FormatError(ValueError):
    pass


def checked_slice(data: bytes, offset: int, size: int) -> bytes:
    if offset < 0 or size < 0 or offset > len(data) or size > len(data) - offset:
        raise FormatError(f"Read outside image: offset={offset:#x}, size={size:#x}")
    return data[offset:offset + size]


def unpack(fmt: str, data: bytes, offset: int = 0) -> tuple:
    return struct.unpack(fmt, checked_slice(data, offset, struct.calcsize(fmt)))


def cstring(data: bytes, offset: int) -> str:
    if not 0 <= offset < len(data):
        raise FormatError(f"String offset outside table: {offset:#x}")
    end = data.find(b"\0", offset)
    if end < 0:
        raise FormatError("Unterminated string")
    return data[offset:end].decode("utf-8", errors="replace")


def read_sfo(data: bytes) -> dict:
    magic, version, keys, values, count = unpack("<5I", data)
    if magic != 0x46535000 or version != 0x101:
        raise FormatError("Unsupported SFO header")
    checked_slice(data, 20, count * 16)
    if not 20 + count * 16 <= keys <= values <= len(data):
        raise FormatError("Invalid SFO table layout")
    result = {}
    for i in range(count):
        key, kind, length, capacity, value = unpack("<HHIII", data, 20 + i * 16)
        if length > capacity:
            raise FormatError("SFO value exceeds capacity")
        name = cstring(data[keys:values], key)
        raw = checked_slice(data, values + value, length)
        if kind == 0x404:
            if len(raw) != 4:
                raise FormatError("Invalid SFO integer length")
            result[name] = unpack("<I", raw)[0]
        elif kind == 0x204:
            result[name] = raw.rstrip(b"\0").decode("utf-8", errors="replace")
        else:
            result[name] = {"type": kind, "hex": raw.hex()}
    return result


def inspect_pkg(path: Path) -> dict:
    """Read the header and public SFO without scanning multi-GB game assets."""
    file_size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(0x100)
        if checked_slice(header, 0, 4) != b"\x7fCNT":
            raise FormatError("Not a PS4 PKG")
        count = unpack(">I", header, 0x10)[0]
        table = unpack(">I", header, 0x18)[0]
        if count > 100_000 or table + count * 32 > file_size:
            raise FormatError("Invalid PKG entry table")
        stream.seek(table)
        entries_data = stream.read(count * 32)
        entries, sfo = [], None
        for i in range(count):
            eid, name, flags1, flags2, offset, size, _ = unpack(">6IQ", entries_data, i * 32)
            if offset + size > file_size:
                raise FormatError(f"PKG entry {eid:#x} exceeds file")
            entries.append(dict(index=i, id=eid, offset=offset, size=size,
                                encrypted=bool(flags1 & 0x80000000)))
            if eid == 0x1000:
                if flags1 & 0x80000000:
                    raise FormatError("Encrypted PARAM.SFO is unsupported")
                if size > 16 * 1024 * 1024:
                    raise FormatError("Unexpectedly large PARAM.SFO")
                stream.seek(offset)
                sfo = read_sfo(stream.read(size))
    return dict(path=str(path.resolve()), size=file_size,
                content_id=cstring(header, 0x40), entries=entries, sfo=sfo)


PT_LOAD = 1
PT_DYNAMIC = 2
PT_TLS = 7
PT_SCE_DYNLIBDATA = 0x61000000
PT_SCE_RELRO = 0x61000010
PT_GNU_EH_FRAME = 0x6474E550
PH_NAMES = {1: "LOAD", 2: "DYNAMIC", 3: "INTERP", 7: "TLS",
            0x61000000: "SCE_DYNLIBDATA", 0x61000001: "SCE_PROCPARAM",
            0x61000002: "SCE_MODULE_PARAM", 0x61000010: "SCE_RELRO",
            0x6474E550: "GNU_EH_FRAME", 0x6FFFFF00: "SCE_COMMENT",
            0x6FFFFF01: "SCE_LIBVERSION"}


@dataclass(frozen=True)
class Segment:
    type: int
    flags: int
    offset: int
    vaddr: int
    paddr: int
    filesz: int
    memsz: int
    align: int

    def describe(self) -> dict:
        return dict(asdict(self), name=PH_NAMES.get(self.type, hex(self.type)))


class ElfImage:
    """Reads ELF offsets through SELF segment mappings without assuming sections."""
    def __init__(self, data: bytes):
        self.data = data
        self.is_self = data[:4] == b"\x4f\x15\x3d\x1d"
        self.mappings = []
        if self.is_self:
            checked_slice(data, 0, 32)
            if data[4:10] != b"\0\1\1\x12\1\1":
                raise FormatError("Unsupported SELF header attributes")
            count = unpack("<H", data, 24)[0]
            if count > 4096:
                raise FormatError("Excessive SELF segment count")
            self.elf_offset = 32 + count * 32
            self.self_segments = [unpack("<4Q", data, 32 + i * 32) for i in range(count)]
        else:
            self.elf_offset = 0
            self.self_segments = []
        self.header = unpack("<16sHHIQQQIHHHHHH", data, self.elf_offset)
        ident, self.type, self.machine, version, self.entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = self.header
        if ident[:7] != b"\x7fELF\2\1\1" or self.machine != 62 or version != 1:
            raise FormatError("Expected a little-endian x86-64 ELF")
        if ehsize != 64 or phsize != 56 or phnum > 4096:
            raise FormatError("Unsupported ELF header sizes")
        self.segments = [Segment(*unpack("<II6Q", data, self.elf_offset + phoff + i * phsize))
                         for i in range(phnum)]
        for seg in self.segments:
            if seg.type in (PT_LOAD, PT_SCE_RELRO) and seg.filesz > seg.memsz:
                raise FormatError("File-backed bytes exceed mapped memory")
            if seg.align and seg.align & (seg.align - 1):
                raise FormatError("Segment alignment is not a power of two")
        for flags, offset, size, memsize in self.self_segments:
            if not flags & 0x800:
                continue  # Hash/signature records do not contain program bytes.
            index = (flags >> 20) & 0xFFF
            if index >= len(self.segments):
                raise FormatError("SELF segment refers to invalid program header")
            if flags & 0xA:
                raise FormatError("Encrypted or compressed SELF program segments are unsupported; a decrypted executable is required")
            ph = self.segments[index]
            if size != memsize or size != ph.filesz:
                raise FormatError("SELF segment size does not match ELF program header")
            checked_slice(data, offset, size)
            self.mappings.append((ph.offset, size, offset))
        # Ensure every segment used for execution, TLS, imports or unwind lookup is readable.
        for ph in self.segments:
            if ph.type in (PT_LOAD, PT_DYNAMIC, PT_TLS, PT_SCE_RELRO, PT_SCE_DYNLIBDATA, PT_GNU_EH_FRAME) and ph.filesz:
                self.file_bytes(ph.offset, ph.filesz)

    def file_bytes(self, offset: int, size: int) -> bytes:
        if size == 0:
            return b""
        if not self.is_self:
            return checked_slice(self.data, offset, size)
        for elf_start, length, self_start in self.mappings:
            if elf_start <= offset and offset + size <= elf_start + length:
                return checked_slice(self.data, self_start + offset - elf_start, size)
        raise FormatError(f"Unmapped SELF range: offset={offset:#x}, size={size:#x}")

    def at_va(self, va: int, size: int) -> bytes:
        for ph in self.segments:
            if ph.type in (PT_LOAD, PT_SCE_RELRO) and ph.vaddr <= va and va + size <= ph.vaddr + ph.filesz:
                return self.file_bytes(ph.offset + va - ph.vaddr, size)
        raise FormatError(f"Virtual address is not file-backed: {va:#x} (+{size:#x})")

    def unwrap(self) -> tuple[bytes, list[str]]:
        """Produce an analysis ELF, reporting any unavailable non-runtime metadata."""
        if not self.is_self:
            return self.data, []
        if self.header[6] or self.header[12]:
            raise FormatError("SELF section-table reconstruction is unsupported")
        header_end = self.header[5] + self.header[9] * self.header[10]
        end = max([header_end] + [p.offset + p.filesz for p in self.segments])
        if end > 512 * 1024 * 1024:
            raise FormatError("Analysis ELF exceeds 512 MiB limit")
        out = bytearray(end)
        out[:header_end] = checked_slice(self.data, self.elf_offset, header_end)
        missing = []
        for p in self.segments:
            try:
                out[p.offset:p.offset + p.filesz] = self.file_bytes(p.offset, p.filesz)
            except FormatError:
                if p.type not in (0x6FFFFF00, 0x6FFFFF01):
                    raise
                missing.append(f"{PH_NAMES[p.type]} at {p.offset:#x} unavailable; zero-filled")
        return bytes(out), missing

    def dynamic(self) -> list[tuple[int, int]]:
        result = []
        for ph in self.segments:
            if ph.type != PT_DYNAMIC:
                continue
            raw = self.file_bytes(ph.offset, ph.filesz)
            if len(raw) % 16:
                raise FormatError("Partial dynamic entry")
            for tag, value in struct.iter_unpack("<qQ", raw):
                if tag == 0:
                    break
                result.append((tag, value))
        return result

    def linkage(self) -> dict:
        dyn = self.dynamic()
        tags = dict(dyn)
        if not dyn:
            return dict(needed=[], modules=[], libraries=[], export_modules=[], export_libraries=[], symbols=[], relocations=[])
        phs = [p for p in self.segments if p.type == PT_SCE_DYNLIBDATA]
        if len(phs) != 1:
            raise FormatError("Expected one SCE dynamic data segment")
        base = phs[0]
        def table(offset_tag, size_tag, entry_size):
            offset, size = tags.get(offset_tag, 0), tags.get(size_tag, 0)
            if size % entry_size or offset + size > base.filesz:
                raise FormatError("Invalid SCE dynamic table")
            return self.file_bytes(base.offset + offset, size)
        strings = table(0x61000035, 0x61000037, 1)
        needed = [cstring(strings, value) for tag, value in dyn if tag == 1]
        modules, libraries, export_modules, export_libraries = [], [], [], []
        for tag, value in dyn:
            if tag in (0x6100000F, 0x61000015, 0x6100000D, 0x61000013):
                item = dict(name=cstring(strings, value & 0xFFFFFFFF), id=value >> 48,
                            encoded_id=encode_id(value >> 48), version=(value >> 32) & 0xFFFF)
                {0x6100000F: modules, 0x61000015: libraries,
                 0x6100000D: export_modules, 0x61000013: export_libraries}[tag].append(item)
        library_map = {x["encoded_id"]: x["name"] for x in libraries}
        module_map = {x["encoded_id"]: x["name"] for x in modules}
        export_library_map = {x["encoded_id"]: x["name"] for x in export_libraries}
        export_module_map = {x["encoded_id"]: x["name"] for x in export_modules}
        symbols = []
        if tags.get(0x6100003B, 24) != 24:
            raise FormatError("Unsupported symbol entry size")
        raw = table(0x61000039, 0x6100003F, 24)
        for i, (name, info, other, shndx, value, size) in enumerate(struct.iter_unpack("<IBBHQQ", raw)):
            name = cstring(strings, name)
            parts = name.split("#")
            lib_map = export_library_map if shndx else library_map
            mod_map = export_module_map if shndx else module_map
            symbols.append(dict(index=i, name=name, nid=parts[0], bind=info >> 4,
                                type=info & 15, defined=shndx != 0, value=value, size=size,
                                library=lib_map.get(parts[1], parts[1]) if len(parts) == 3 else None,
                                module=mod_map.get(parts[2], parts[2]) if len(parts) == 3 else None))
        relocations = []
        if tags.get(0x61000033, 24) != 24:
            raise FormatError("Unsupported relocation entry size")
        for offset_tag, size_tag, kind in [(0x6100002F, 0x61000031, "rela"), (0x61000029, 0x6100002D, "plt")]:
            for offset, info, addend in struct.iter_unpack("<QQq", table(offset_tag, size_tag, 24)):
                symbol = info >> 32
                if symbol >= len(symbols):
                    raise FormatError("Relocation symbol index out of bounds")
                relocations.append(dict(offset=offset, type=info & 0xFFFFFFFF,
                                        symbol=symbol, addend=addend, table=kind))
        return dict(needed=needed, modules=modules, libraries=libraries,
                    export_modules=export_modules, export_libraries=export_libraries,
                    symbols=symbols, relocations=relocations)

    def unwind_functions(self) -> list[dict]:
        """Use the actual .eh_frame_hdr index, never a linear disassembly guess.

        This deliberately supports only the encoding present in the inspected build.
        Entries are unwind ranges, not a guarantee of every source-level function.
        """
        headers = [p for p in self.segments if p.type == PT_GNU_EH_FRAME]
        if not headers:
            return []
        ph = headers[0]
        data = self.file_bytes(ph.offset, ph.filesz)
        if data[:4] != b"\x01\x1b\x03\x3b":
            raise FormatError(f"Unsupported EH frame header encoding: {data[:4].hex()}")
        count = unpack("<I", data, 8)[0]
        checked_slice(data, 12, count * 8)
        result = []
        for i in range(count):
            start_delta, fde_delta = unpack("<ii", data, 12 + i * 8)
            start, fde = ph.vaddr + start_delta, ph.vaddr + fde_delta
            # Read the CIE augmentation to verify its FDE address encoding.
            length, cie_delta = unpack("<II", self.at_va(fde, 8))
            if length < 12 or length == 0xFFFFFFFF:
                raise FormatError("Unsupported FDE length")
            self.at_va(fde, length + 4)
            cie = fde + 4 - cie_delta
            cie_len = unpack("<I", self.at_va(cie, 4))[0]
            cie_raw = self.at_va(cie, cie_len + 4)
            if unpack("<I", cie_raw, 4)[0] != 0 or checked_slice(cie_raw, 8, 1)[0] != 1:
                raise FormatError("Unsupported CIE")
            augmentation = cstring(cie_raw, 9)
            cursor = 10 + len(augmentation)
            _, cursor = leb128(cie_raw, cursor)
            _, cursor = leb128(cie_raw, cursor)  # SLEB value unused; same byte extent.
            cursor += 1  # CIE v1 return-address register.
            encoding = 0
            if augmentation.startswith("z"):
                aug_len, cursor = leb128(cie_raw, cursor)
                aug_end = cursor + aug_len
                checked_slice(cie_raw, cursor, aug_len)
                for item in augmentation[1:]:
                    if item in ("L", "R"):
                        value = checked_slice(cie_raw, cursor, 1)[0]
                        cursor += 1
                        if item == "R":
                            encoding = value
                    elif item == "P":
                        ptr_enc = checked_slice(cie_raw, cursor, 1)[0]
                        size = {0: 8, 3: 4, 0xB: 4, 4: 8, 0xC: 8}.get(ptr_enc & 15)
                        if size is None:
                            raise FormatError("Unsupported CIE personality encoding")
                        cursor += 1 + size
                    elif item != "S":
                        raise FormatError(f"Unsupported CIE augmentation: {augmentation}")
                if cursor > aug_end:
                    raise FormatError("CIE augmentation overrun")
            if encoding != 0x1B:
                raise FormatError(f"Unsupported FDE address encoding: {encoding:#x}")
            initial_delta, size = unpack("<iI", self.at_va(fde + 8, 8))
            if fde + 8 + initial_delta != start:
                raise FormatError("FDE and unwind index disagree")
            self.at_va(start, size)
            result.append(dict(start=start, size=size, fde=fde))
        return result


def leb128(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        byte = checked_slice(data, offset, 1)[0]
        offset += 1
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, offset
    raise FormatError("Oversized LEB128")


def encode_id(value: int) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    if not 0 <= value <= 0xFFFF:
        raise FormatError("Invalid library/module ID")
    result = alphabet[value & 63]
    while value >= 64:
        value >>= 6
        result = alphabet[value & 63] + result
    return result
