"""Generate hand-authored CPU cases for native differential validation.

No game data is used. Cases exercise register aliases, sign extension, wrapping
arithmetic, masked shifts, rotations and byte order against the actual x64 CPU.
"""
import json
from pathlib import Path
from tools.recompile import emit_functions, lift


CASES = {
    'copy64': '4889f8c3',
    'zero_extend32': '89f8c3',
    'partial_high8': '89f888ccc3',
    'partial_low16': '89f86689f0c3',
    'sign8_to32': '400fbec7c3',
    'sign8_to64': '480fbec7c3',
    'sign16_to32': '0fbfc6c3',
    'sign32_to64': '4863c7c3',
    'multiply16': '89f8660fafc6c3',
    'multiply64': '4889f8480fafc6c3',
    'multiply_signed_immediate': '486bc7f9c3',
    'left64': '4889f848d3e0c3',
    'right64': '4889f848d3e8c3',
    'arithmetic_right64': '4889f848d3f8c3',
    'rotate_left64': '4889f848d3c0c3',
    'rotate_right64': '4889f848d3c8c3',
    'left32': '89f8d3e0c3',
    'right32': '89f8d3e8c3',
    'arithmetic_right32': '89f8d3f8c3',
    'rotate_left32': '89f8d3c0c3',
    'rotate_right32': '89f8d3c8c3',
    'negative32': '89f8f7d8c3',
    'invert64': '4889f848f7d0c3',
    'swap64': '4889f8480fc8c3',
    'swap32': '89f80fc8c3',
    'cdqe': '89f84898c3',
    'lea32_addressing': '67488d04bec3',
    'zero_idiom': '31c0b001c3',
}


def main():
    output = Path('local/selftest')
    selected = []
    for index, (name, hex_code) in enumerate(CASES.items(), start=1):
        cpp, operations, disassembly = lift(bytes.fromhex(hex_code), index)
        selected.append(dict(start=index, name=name, bytes=hex_code, cpp=cpp,
                             operations=operations, disassembly=disassembly))
    emit_functions(selected, output)
    (output / 'cases.json').write_text(json.dumps([{k: v for k, v in s.items() if k != 'cpp'} for s in selected], indent=2))
    print(f'Generated {len(selected)} synthetic instruction tests.')


if __name__ == '__main__':
    main()
