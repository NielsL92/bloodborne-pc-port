"""Independent exact-byte checks for the 11-bit implicit x87 opcode immediate."""
import json,subprocess,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);lifter=Path(sys.argv[2]).resolve();semantics=Path(sys.argv[3]).resolve()
rows=[];roots=[];expected=[];decoded=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for prefix in ['', '66','67','48','64','6648','65674f']:
 for opcode in range(0xd8,0xe0):
  # The low opcode byte is a ModRM; memory forms have no trailing displacement.
  for modrm in [0x00,0x01]:
   code=bytes.fromhex(prefix)+bytes([opcode,modrm]);pc=0x100090000+len(roots)*32
   ins=list(decoder.disasm(code,pc));assert len(ins)==1 and ins[0].size==len(code),code.hex()
   roots.append(pc);rows.extend([dict(address=pc,bytes=code.hex()),dict(address=pc+len(code),bytes='c3')]);expected.append(dict(address=pc,original=((opcode&3)<<8)|modrm,corrected=((opcode&7)<<8)|modrm));decoded.append(dict(address=pc,bytes=code.hex(),mnemonic=ins[0].mnemonic,operands=ins[0].op_str))
write_json(out/'input.json',dict(roots=roots,instructions=rows));write_json(out/'independent-decode.json',decoded)
argv=[str(lifter),str(out/'input.json'),str(out/'function.bc'),str(out/'function.ll'),str(out/'audit.json'),str(semantics)]
with (out/'lift.stdout').open('wb') as stdout,(out/'lift.stderr').open('wb') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=180)
write_json(out/'steps.json',[dict(argv=argv,exit_code=r.returncode)]);assert r.returncode==0
audit=json.loads((out/'audit.json').read_text(encoding='utf-8'));assert audit['x87_opcode_immediates']==expected and len(audit['decoded_addresses'])==224 and not audit['missing_instruction_starts'] and not audit['unvisited_manifest_instructions']
summary=dict(status='all exact-byte x87 opcode checks passed',cases=len(expected),corrected_cases=sum(x['original']!=x['corrected'] for x in expected),lifter_sha256=sha(lifter),semantics_sha256=sha(semantics/'amd64_avx.bc'),audit_sha256=sha(out/'audit.json'),independent_decode_sha256=sha(out/'independent-decode.json'),execution='none; authored static input only, not execution coverage')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
