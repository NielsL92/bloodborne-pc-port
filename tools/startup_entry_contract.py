"""Cross-check supplied startup bytes and bound the first native entry probe."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
source=Path('local/cfg/startup-recovery-v31-conditional-repeat');ghidra=Path('local/cfg/ghidra-startup-entry-v1');windows=Path('local/runtime/startup-entry-windows-v1');plan=Path('local/runtime/loader-plan-v8-memory');registry=Path('local/runtime/registry-v7-memory-repeat');modules=read(plan/'modules.json');decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True;c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);checked=[];instructions={}
for module in modules:
 file=ghidra/module['name']/'ghidra.json'
 if not file.exists():continue
 assert sha(module['path'])==module['module'];im=ElfImage(Path(module['path']).read_bytes())
 for window in read(file):
  for row in window['instructions']:
   raw=im.at_va(row['rva'],row['length']);assert raw.hex()==row['bytes'];ins=next(decoder.disasm(raw,row['rva'],count=1));assert ins.size==row['length'];instructions[module['name'],row['rva']]=dict(**row,capstone=ins.mnemonic+' '+ins.op_str);checked.append(dict(module=module['module'],**row))
  for rva,code in c.execute('select rva,bytes from recovery_instruction where module=? and rva>=? and rva<?',(module['module'],window['start'],window['end'])):assert instructions[module['name'],rva]['bytes']==code
main=next(m for m in modules if m['name']=='eboot.bin');libc=next(m for m in modules if m['name']=='libc.prx');assert main['entry_rva']==0xa0
for at,code in [(0xa0,'55'),(0xa1,'4889e5'),(0xa4,'4157'),(0xa6,'4156'),(0xa8,'53'),(0xa9,'50'),(0xaa,'4889f3'),(0xad,'448b37'),(0xb0,'4c8d7f08'),(0xb4,'e8ffe3bb02'),(0xb9,'4889df'),(0xbc,'e807e4bb02')]:assert instructions['eboot.bin',at]['bytes']==code
assert instructions['libc.prx',0x5fef0]['text']=='RET';load=instructions['libc.prx',0x2f119];ins=next(decoder.disasm(bytes.fromhex(load['bytes']),0x2f119,count=1));assert ins.operands[1].type==X86_OP_MEM and ins.operands[1].mem.base==X86_REG_RIP;slot=ins.address+ins.size+ins.operands[1].mem.disp;assert f'0x{slot:08x}' in load['text'];unresolved=next(r for r in read(plan/'unresolved-relocations.json') if r['module']==libc['module'] and r['offset']==slot);assert unresolved['symbol']['nid']=='f7uOxY9mM1U' and unresolved['symbol']['type']==1 and unresolved['value'] is None
contract=dict(status='entry prefix and first compiled libc calls independently checked',registry_identity=sha(registry/'identity.json'),loader_plan_sha256=sha(plan/'summary.json'),ghidra_summary_sha256=sha(ghidra/'summary.json'),checked_instructions=len(checked),entry_pc=main['entry_pc'],parameter_prefix=dict(argc_offset=0,argc_size=4,argv_offset=8,exit_callback_register='RSI',provenance='Exact supplied main-entry loads; full EntryParams layout is a separately labeled baseline reference.'),initial_rsp_mod16=8,stack_base=0x70000000000,stack_size=0x100000,parameter_base=0x70000200000,parameter_size=0x2000,exit_callback_pc=0x9fffffff0,argc=1,argv0='/app0/eboot.bin',expected_stop=dict(source=libc['logical_base']+0x2f119,address=libc['logical_base']+slot,width=8,unresolved_identity=f"{libc['module']}:{slot:x}:{unresolved['type']}",completed_memory_operations=11,rsp_decrement=104,active_import=0x102bbe4c8,nid='8G2LB+A3rzg'),game_execution=False,limitations=['This is a bounded entry probe with explicitly chosen private process parameters, not proof of complete platform startup ABI or module initialization order.','Other State fields start at zero; no target FP profile or per-thread TLS is selected. The checked prefix uses neither.','The native exit callback is an explicit diagnostic stop; it is not a implemented process teardown.','The expected canary-slot stop precedes callback registration, constructor calls and main. No service success stub or original-byte CPU execution is allowed.'])
write_json(a.out/'checked-instructions.json',checked);write_json(a.out/'contract.json',contract);print(json.dumps(contract),flush=True)
