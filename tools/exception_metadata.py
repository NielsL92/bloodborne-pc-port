"""Bounded readers for the observed CIE/FDE and GCC LSDA encodings.

Reference: LLVM libcxxabi/src/cxa_personality.cpp exception table layout.
Produces static metadata, not an implementation of exception propagation.
"""
import struct
from tools.formats import FormatError, checked_slice, cstring, leb128, unpack

def sleb(data, offset):
    begin = offset
    value, offset = leb128(data, offset)
    if data[offset-1] & 64:
        value -= 1 << (7 * (offset-begin))
    return value, offset

def scalar(data, offset, encoding):
    if encoding == 1:
        return leb128(data, offset)
    if encoding == 9:
        return sleb(data, offset)
    fmt = {0:"<Q",2:"<H",3:"<I",4:"<Q",10:"<h",11:"<i",12:"<q"}.get(encoding)
    if fmt is None:
        raise FormatError(f"unsupported scalar encoding {encoding:#x}")
    return unpack(fmt, data, offset)[0], offset+struct.calcsize(fmt)

def cie_metadata(image, address):
    size = unpack("<I", image.at_va(address, 4))[0]
    if size < 9 or size > 65536:
        raise FormatError("invalid CIE size")
    raw = image.at_va(address, size+4)
    if unpack("<I", raw, 4)[0] != 0 or raw[8] != 1:
        raise FormatError("unsupported CIE ID/version")
    aug = cstring(raw, 9)
    cursor = 10 + len(aug)
    _, cursor = leb128(raw, cursor)
    _, cursor = sleb(raw, cursor)
    checked_slice(raw, cursor, 1)
    cursor += 1
    if aug not in ("zR", "zPLR"):
        raise FormatError(f"unsupported CIE augmentation {aug}")
    length, cursor = leb128(raw, cursor)
    end = cursor+length
    checked_slice(raw, cursor, length)
    personality = None
    lsda_encoding = 255
    if aug == "zPLR":
        enc = raw[cursor]; cursor += 1
        if enc != 0x9b:
            raise FormatError(f"unsupported personality encoding {enc:#x}")
        # Keep the indirection slot, not its unrelocated file contents.
        personality = address+cursor+unpack("<i", raw, cursor)[0]
        cursor += 4
        lsda_encoding = raw[cursor]; cursor += 1
        if lsda_encoding != 0x1b:
            raise FormatError(f"unsupported LSDA encoding {lsda_encoding:#x}")
    fde_encoding = raw[cursor]; cursor += 1
    if fde_encoding != 0x1b or cursor != end:
        raise FormatError("unsupported FDE encoding or augmentation extent")
    return dict(cie=address, augmentation=aug, lsda_encoding=lsda_encoding,
                personality_slot=personality)

def fde_metadata(image, fn, cache):
    address = fn["fde"]
    length, delta = unpack("<II", image.at_va(address, 8))
    if length < 12 or length > 65536:
        raise FormatError("invalid FDE size")
    raw = image.at_va(address, length+4)
    cie = address+4-delta
    if cie not in cache:
        cache[cie] = cie_metadata(image, cie)
    c = cache[cie]
    relative, size = unpack("<iI", raw, 8)
    if address+8+relative != fn["start"] or size != fn["size"]:
        raise FormatError("FDE/index disagreement")
    aug_len, cursor = leb128(raw, 16)
    checked_slice(raw, cursor, aug_len)
    result = dict(c, fde=address, start=fn["start"], size=size, lsda=None)
    if c["lsda_encoding"] == 255:
        if aug_len:
            raise FormatError("unexpected FDE augmentation")
        return result
    if aug_len != 4:
        raise FormatError("unsupported LSDA augmentation extent")
    value = unpack("<i", raw, cursor)[0]
    result["lsda"] = address+cursor+value if value else None
    return result

def lsda_metadata(image, fde):
    address = fde["lsda"]
    if address is None:
        return None
    # A view confined to the containing file-backed segment; cap malformed tables.
    segment = next((s for s in image.segments
                    if s.vaddr <= address < s.vaddr+s.filesz), None)
    if segment is None:
        raise FormatError("LSDA outside file-backed mappings")
    raw = image.at_va(address, min(segment.vaddr+segment.filesz-address, 1024*1024))
    cursor = 0
    lp_encoding = checked_slice(raw,cursor,1)[0]; cursor += 1
    if lp_encoding != 255:
        raise FormatError(f"unsupported LPStart encoding {lp_encoding:#x}")
    lp_start = fde["start"]
    type_encoding = checked_slice(raw,cursor,1)[0]; cursor += 1
    type_base = None
    if type_encoding != 255:
        offset, cursor = leb128(raw,cursor)
        type_base = cursor+offset
        checked_slice(raw,type_base,0)
    call_encoding = checked_slice(raw,cursor,1)[0]; cursor += 1
    if call_encoding not in (1,2,3,4):
        raise FormatError(f"unsupported call-site encoding {call_encoding:#x}")
    length, cursor = leb128(raw,cursor)
    table_start = cursor
    end = cursor+length
    checked_slice(raw,cursor,length)
    if type_base is not None and type_base < end:
        raise FormatError("type table overlaps call-site records")
    table = raw[:end]
    records = []
    previous_end = 0
    while cursor < end:
        record_rva = address+cursor
        start,cursor = scalar(table,cursor,call_encoding)
        length,cursor = scalar(table,cursor,call_encoding)
        landing,cursor = scalar(table,cursor,call_encoding)
        action,cursor = leb128(table,cursor)
        if start < previous_end or start+length > fde["size"]:
            raise FormatError("overlapping/out-of-range call-site interval")
        previous_end = start+length
        if landing and not fde["start"] <= lp_start+landing < fde["start"]+fde["size"]:
            raise FormatError("landing pad outside indexed range")
        records.append(dict(record_rva=record_rva,start=fde["start"]+start,
                            length=length,landing_pad=lp_start+landing if landing else None,
                            action=action))
    if cursor != end:
        raise FormatError("call-site table overrun")
    # Decode referenced action chains only. Type indices remain unresolved metadata.
    action_limit = type_base if type_base is not None else len(raw)
    actions = {}
    for record in records:
        if not record["action"]:
            continue
        cursor = end+record["action"]-1
        seen = set()
        while True:
            if cursor < end or cursor >= action_limit or cursor in seen or len(seen) >= 4096:
                raise FormatError("invalid/cyclic LSDA action chain")
            seen.add(cursor)
            action_rva = address+cursor
            filter_value, cursor = sleb(raw[:action_limit],cursor)
            next_field = cursor
            next_delta, cursor = sleb(raw[:action_limit],cursor)
            actions[action_rva] = dict(rva=action_rva,type_filter=filter_value,
                                      next_rva=address+next_field+next_delta if next_delta else None)
            if not next_delta:
                break
            cursor = next_field+next_delta
    return dict(lsda=address,lp_start=lp_start,lp_encoding=lp_encoding,
                type_encoding=type_encoding,type_table=address+type_base if type_base is not None else None,
                call_encoding=call_encoding,call_table_start=address+table_start,
                call_table_end=address+end,call_sites=records,actions=list(actions.values()))
