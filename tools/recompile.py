"""Conservative static translation of register-only x64 leaf functions to C++.

This is a bounded proof, not a whole-program recompiler. Unsupported semantics
are rejected, never replaced with stubs. Generated files remain under local/.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_REG, X86_OP_IMM, X86_OP_MEM

from tools.formats import ElfImage, FormatError


class Unsupported(ValueError):
    pass


ALIASES = {}
for names in [('rax', 'eax', 'ax', 'al', 'ah'), ('rcx', 'ecx', 'cx', 'cl', 'ch'),
              ('rdx', 'edx', 'dx', 'dl', 'dh'), ('rsi', 'esi', 'si', 'sil'),
              ('rdi', 'edi', 'di', 'dil')]:
    for name, width, shift in zip(names, (64, 32, 16, 8, 8), (0, 0, 0, 0, 8)):
        ALIASES[name] = (names[0], width, shift)
for number in range(8, 12):
    for suffix, width in [('', 64), ('d', 32), ('w', 16), ('b', 8)]:
        ALIASES[f'r{number}{suffix}'] = (f'r{number}', width, 0)
ARG_REGS = ('rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9')
ALL_REGS = ('rax', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11')


def literal(value: int) -> str:
    return f'UINT64_C(0x{value & ((1 << 64) - 1):x})'


class Lifter:
    def __init__(self):
        self.initialized = set(ARG_REGS)
        self.lines = []
        self.operations = 0

    def alias(self, ins, operand):
        if operand.type != X86_OP_REG:
            raise Unsupported('non-register destination')
        name = ins.reg_name(operand.reg)
        if name not in ALIASES:
            raise Unsupported('unsupported register')
        return ALIASES[name]

    def read_reg(self, name):
        if name not in ALIASES:
            raise Unsupported('unsupported register')
        base, width, shift = ALIASES[name]
        if base not in self.initialized:
            raise Unsupported('read of unspecified incoming register')
        if width == 64:
            return base
        return f'(({base} >> {shift}) & {literal((1 << width) - 1)})'

    def read(self, ins, op):
        if op.type == X86_OP_IMM:
            return literal(op.imm)
        if op.type == X86_OP_REG:
            return self.read_reg(ins.reg_name(op.reg))
        raise Unsupported('memory access')

    def write(self, ins, op, expression):
        base, width, shift = self.alias(ins, op)
        if width in (32, 64):
            self.lines.append(f'    {base} = static_cast<uint{width}_t>({expression});')
            self.initialized.add(base)
        else:
            if base not in self.initialized:
                raise Unsupported('partial write to unspecified register')
            mask = ((1 << width) - 1) << shift
            self.lines.append(f'    {base} = ({base} & ~{literal(mask)}) | ((static_cast<uint64_t>({expression}) << {shift}) & {literal(mask)});')

    def translate(self, ins):
        m, ops = ins.mnemonic, ins.operands
        if ins.prefix[0] != 0:
            raise Unsupported('instruction prefix')
        if m == 'nop':
            return
        if m == 'ret':
            if ops:
                raise Unsupported('return with stack adjustment')
            if 'rax' not in self.initialized:
                raise Unsupported('unspecified return value')
            return
        if m == 'cdqe':
            value = self.read_reg('eax')
            self.lines.append(f'    rax = sign_extend({value}, 32);')
            self.initialized.add('rax')
            return
        if not ops:
            raise Unsupported('unsupported instruction')
        _, width, _ = self.alias(ins, ops[0])
        if m in ('mov', 'movabs', 'movzx') and len(ops) == 2:
            self.write(ins, ops[0], self.read(ins, ops[1]))
        elif m in ('movsx', 'movsxd') and len(ops) == 2:
            self.write(ins, ops[0], f'sign_extend({self.read(ins, ops[1])}, {ops[1].size * 8})')
        elif m == 'lea' and len(ops) == 2 and ops[1].type == X86_OP_MEM:
            mem = ops[1].mem
            if mem.segment:
                raise Unsupported('segment addressing')
            parts = [literal(mem.disp)]
            if mem.base:
                parts.append(self.read_reg(ins.reg_name(mem.base)))
            if mem.index:
                parts.append(f'({self.read_reg(ins.reg_name(mem.index))} * {mem.scale})')
            if ins.addr_size not in (4, 8):
                raise Unsupported('address width')
            self.write(ins, ops[0], f'static_cast<uint{ins.addr_size * 8}_t>({" + ".join(parts)})')
            self.operations += 1
        elif m in ('add', 'sub', 'and', 'or', 'xor') and len(ops) == 2:
            # A zero idiom does not depend on the incoming register value.
            if m == 'xor' and ops[1].type == X86_OP_REG and ops[0].reg == ops[1].reg:
                expression = 'UINT64_C(0)'
            else:
                operator = {'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'xor': '^'}[m]
                expression = f'({self.read(ins, ops[0])} {operator} {self.read(ins, ops[1])})'
            self.write(ins, ops[0], expression)
            self.operations += 1
        elif m == 'imul' and len(ops) in (2, 3):
            left, right = (ops[0], ops[1]) if len(ops) == 2 else (ops[1], ops[2])
            self.write(ins, ops[0], f'({self.read(ins, left)} * {self.read(ins, right)})')
            self.operations += 1
        elif m in ('shl', 'sal', 'shr', 'sar', 'rol', 'ror') and len(ops) == 2 and width in (32, 64):
            value = self.read(ins, ops[0])
            count = f'({self.read(ins, ops[1])} & {width - 1})'
            if m in ('shl', 'sal', 'shr'):
                expression = f'({value} {">>" if m == "shr" else "<<"} {count})'
            elif m == 'sar':
                expression = f'arithmetic_shift({value}, static_cast<unsigned>({count}), {width})'
            else:
                expression = f'std::{"rotl" if m == "rol" else "rotr"}(static_cast<uint{width}_t>({value}), static_cast<int>({count}))'
            self.write(ins, ops[0], expression)
            self.operations += 1
        elif m in ('not', 'neg', 'bswap') and len(ops) == 1:
            value = self.read(ins, ops[0])
            if m == 'not':
                expression = f'~({value})'
            elif m == 'neg':
                expression = f'(UINT64_C(0) - {value})'
            elif width in (32, 64):
                expression = f'byte_swap({value}, {width // 8})'
            else:
                raise Unsupported('byte-swap width')
            self.write(ins, ops[0], expression)
            self.operations += 1
        else:
            raise Unsupported('unsupported instruction')


def lift(code: bytes, address: int, decoder=None) -> tuple[str, int, list[str]]:
    if decoder is None:
        decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        decoder.detail = True
    instructions = list(decoder.disasm(code, address))
    if not instructions or sum(i.size for i in instructions) != len(code):
        raise Unsupported('incomplete instruction decoding')
    if instructions[-1].mnemonic != 'ret' or any(i.mnemonic == 'ret' for i in instructions[:-1]):
        raise Unsupported('not a straight-line leaf')
    lifter = Lifter()
    for ins in instructions:
        lifter.translate(ins)
    declaration = [f'static uint64_t recomp_{address:x}(const uint64_t* args) {{']
    declaration += [f'    [[maybe_unused]] uint64_t {reg} = args[{i}];' for i, reg in enumerate(ARG_REGS)]
    declaration += [f'    [[maybe_unused]] uint64_t {reg};' for reg in ALL_REGS if reg not in ARG_REGS]
    declaration += lifter.lines
    declaration += ['    return rax;', '}']
    return '\n'.join(declaration), lifter.operations, [f'{i.address:x}: {i.mnemonic} {i.op_str}' for i in instructions]


HELPERS = r'''
#include <bit>
#include <cstdint>
[[maybe_unused]] static uint64_t sign_extend(uint64_t value, unsigned width) {
    if (width == 64) return value;
    const uint64_t mask = (UINT64_C(1) << width) - 1;
    const uint64_t sign = UINT64_C(1) << (width - 1);
    return ((value & mask) ^ sign) - sign;
}
[[maybe_unused]] static uint64_t arithmetic_shift(uint64_t value, unsigned count, unsigned width) {
    if (width == 32) value &= UINT64_C(0xffffffff);
    if (count == 0) return value;
    return (value >> count) | ((value >> (width - 1)) ? (~UINT64_C(0) << (width - count)) : 0);
}
[[maybe_unused]] static uint64_t byte_swap(uint64_t value, unsigned bytes) {
    uint64_t out = 0;
    for (unsigned i = 0; i < bytes; ++i) { out = (out << 8) | (value & 255); value >>= 8; }
    return out;
}
'''


def emit_functions(selected: list[dict], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    content = ['// Generated locally. Game-derived code, if present, must remain local.', HELPERS]
    entries = []
    for fn in selected:
        address = fn['start']
        content.append(fn['cpp'])
        bytes_text = ','.join('0x' + fn['bytes'][i:i+2] for i in range(0, len(fn['bytes']), 2))
        content.append(f'static constexpr unsigned char original_{address:x}[] = {{{bytes_text}}};')
        entries.append(f'    {{{literal(address)}, original_{address:x}, sizeof(original_{address:x}), recomp_{address:x}}},')
    content += ['static constexpr ProofFunction proof_functions[] = {', *entries, '};']
    (output / 'functions.inc').write_text('\n\n'.join(content), encoding='utf-8')


def run(eboot: Path, output: Path, max_functions: int, min_ops: int) -> dict:
    raw = eboot.read_bytes()
    image = ElfImage(raw)
    functions = image.unwind_functions()
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True
    rejected = Counter()
    accepted = []
    for fn in functions:
        if not 12 <= fn['size'] <= 140:
            rejected['outside size window'] += 1
            continue
        code = image.at_va(fn['start'], fn['size'])
        try:
            cpp, ops, disassembly = lift(code, fn['start'], decoder)
            if ops < min_ops:
                rejected['below arithmetic-operation threshold'] += 1
                continue
        except Unsupported as error:
            rejected[str(error)] += 1
            continue
        accepted.append(dict(fn, cpp=cpp, operations=ops, bytes=code.hex(),
                             sha256=hashlib.sha256(code).hexdigest(), disassembly=disassembly))
    accepted.sort(key=lambda x: (-x['operations'], x['start']))
    selected = accepted[:max_functions]
    if not selected:
        raise Unsupported('No supported functions found')
    emit_functions(selected, output)
    manifest = dict(status='limited_scalar_static_recompilation_proof',
                    input_sha256=hashlib.sha256(raw).hexdigest(),
                    scope='Straight-line integer register-only leaf functions, six System V integer inputs and RAX output; no stack, memory loads/stores, branches, calls, flags consumers, floating point, SIMD, TLS, GPU or OS services.',
                    total_unwind_ranges=len(functions), eligible_functions=len(accepted),
                    generated_functions=len(selected), rejected=dict(rejected),
                    functions=[{k: v for k, v in fn.items() if k != 'cpp'} for fn in selected])
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'functions'}, indent=2))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eboot', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path('local/recompiled'))
    parser.add_argument('--max-functions', type=int, default=64)
    parser.add_argument('--min-ops', type=int, default=4)
    args = parser.parse_args()
    if args.max_functions < 1 or args.min_ops < 0:
        parser.error('Invalid selection limits')
    try:
        run(args.eboot, args.out, args.max_functions, args.min_ops)
    except (FormatError, OSError, Unsupported) as error:
        parser.exit(1, f'Recompilation failed: {error}\n')


if __name__ == '__main__':
    main()
