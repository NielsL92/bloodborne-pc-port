"""Inventory this project's local game dump. Never executes guest code."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

from tools.formats import ElfImage, FormatError, inspect_pkg


def source_revision(path: Path) -> str | None:
    if not (path / '.git').exists():
        return None
    result = subprocess.run(['git', '-c', f'safe.directory={path.resolve().as_posix()}',
                             '-C', str(path), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def nid_index(source: Path) -> tuple[dict, set]:
    names, registered = {}, set()
    aerolib = source / 'src/core/aerolib/aerolib.inl'
    if aerolib.exists():
        for nid, name in re.findall(r'STUB\(\s*"([^"]+)"\s*,\s*([\w$]+)\s*\)', aerolib.read_text(encoding='utf-8')):
            names[nid] = name
    for path in (source / 'src/core/libraries').rglob('*.cpp'):
        raw = path.read_text(encoding='utf-8', errors='replace')
        for nid, lib in re.findall(r'LIB_(?:FUNCTION|OBJ)\(\s*"([^"]+)"\s*,\s*"([^"]+)"', raw):
            registered.add((nid, lib))
    return names, registered


def run(eboot: Path, packages: list[Path], source: Path, output: Path, modules_dir: Path | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    raw = eboot.read_bytes()
    image = ElfImage(raw)
    links = image.linkage()
    functions = image.unwind_functions()
    names, registered = nid_index(source)
    bundled_modules, bundled_exports = [], {}
    if modules_dir and modules_dir.exists():
        for module in sorted(modules_dir.iterdir()):
            if module.suffix.lower() not in ('.prx', '.sprx'):
                continue
            module_raw = module.read_bytes()
            try:
                module_links = ElfImage(module_raw).linkage()
                module_imports = [s for s in module_links['symbols'] if s['name'] and not s['defined']]
                module_exports = [s for s in module_links['symbols'] if s['name'] and s['defined']]
                for symbol in module_exports:
                    bundled_exports.setdefault((symbol['nid'], symbol['library']), []).append(module.name)
                bundled_modules.append(dict(file=module.name, status='readable',
                                            sha256=hashlib.sha256(module_raw).hexdigest(),
                                            imports=len(module_imports), exports=len(module_exports),
                                            needed=module_links['needed']))
            except FormatError as error:
                bundled_modules.append(dict(file=module.name, status='unsupported', reason=str(error)))
    imports = [s.copy() for s in links['symbols'] if s['name'] and not s['defined']]
    for item in imports:
        item['resolved_name'] = names.get(item['nid'])
        item['shadps4_registration_found'] = (item['nid'], item['library']) in registered
        item['bundled_export_candidates'] = bundled_exports.get((item['nid'], item['library']), [])
    by_lib = Counter(s['library'] for s in imports)
    package_info = [inspect_pkg(p) for p in packages]
    title_ids = {p['sfo']['TITLE_ID'] for p in package_info if p['sfo']}
    if len(title_ids) > 1:
        raise FormatError('Base game and update have different title IDs')
    relocated_imports = {r['symbol'] for r in links['relocations'] if r['symbol']}
    output_elf, omitted = image.unwrap()
    summary = dict(
        status='analysis_only_not_a_playable_port',
        executable=str(eboot.resolve()), sha256=hashlib.sha256(raw).hexdigest(),
        file_bytes=len(raw), architecture='x86-64', elf_type=hex(image.type),
        entry_rva=hex(image.entry), is_self=image.is_self,
        load_segments=[p.describe() for p in image.segments if p.type in (1, 0x61000010)],
        all_segments=[p.describe() for p in image.segments],
        import_count=len(imports), import_libraries=dict(by_lib.most_common()),
        declared_module_count=len(links['needed']), declared_modules=links['needed'],
        symbols_with_names=sum(bool(i['resolved_name']) for i in imports),
        symbols_with_shadps4_registration=sum(i['shadps4_registration_found'] for i in imports),
        symbols_with_bundled_export_candidates=sum(bool(i['bundled_export_candidates']) for i in imports),
        symbols_without_candidates=[i['resolved_name'] or i['name'] for i in imports
                                    if not i['shadps4_registration_found'] and not i['bundled_export_candidates']],
        bundled_modules=bundled_modules,
        imported_symbols_referenced_by_relocations=sum(i['index'] in relocated_imports for i in imports),
        registration_caveat='Static name/NID/library lookup only; it does not validate module versions, signatures, behavior, transitive imports, runtime loading or implementation. Registered functions may be stubs.',
        relocation_count=len(links['relocations']),
        relocation_types=dict(Counter(str(r['type']) for r in links['relocations'])),
        unwind_range_count=len(functions),
        unwind_caveat='Unwind ranges do not establish complete function coverage or source-level identities.',
        tls=[p.describe() for p in image.segments if p.type == 7],
        elf_reconstruction_notes=omitted,
        shadps4_commit=source_revision(source),
        liborbispkg_commit=source_revision(source.parent / 'LibOrbisPkg'),
        packages=package_info)
    (output / 'inventory.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    (output / 'functions.json').write_text(json.dumps(functions), encoding='utf-8')
    (output / 'imports.json').write_text(json.dumps(imports, indent=2), encoding='utf-8')
    (output / 'eboot.elf').write_bytes(output_elf)
    with (output / 'imports.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(imports[0]) if imports else [])
        writer.writeheader()
        writer.writerows(imports)
    print(json.dumps({key: summary[key] for key in (
        'sha256', 'import_count', 'declared_module_count', 'symbols_with_names',
        'symbols_with_shadps4_registration', 'relocation_count', 'unwind_range_count',
        'shadps4_commit', 'elf_reconstruction_notes')}, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eboot', type=Path, required=True)
    parser.add_argument('--pkg', type=Path, action='append', default=[])
    parser.add_argument('--shadps4', type=Path, default=Path('external/shadPS4'))
    parser.add_argument('--out', type=Path, default=Path('local/analysis'))
    parser.add_argument('--modules', type=Path, default=Path('local/base-code/uroot/sce_module'))
    args = parser.parse_args()
    try:
        run(args.eboot, args.pkg, args.shadps4, args.out, args.modules)
    except (FormatError, OSError) as error:
        parser.exit(1, f'Analysis failed: {error}\n')


if __name__ == '__main__':
    main()
