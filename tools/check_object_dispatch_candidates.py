"""Check object-table source operands and independent initial relocation reads."""
import argparse,json,re,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--proposals',type=Path,default=root/'local/cfg/object-dispatch-proposals-v1');p.add_argument('--ghidra',type=Path,default=root/'local/cfg/ghidra-object-dispatch-sources-v1');p.add_argument('--tables',type=Path,default=root/'local/cfg/ghidra-object-dispatch-tables-v1');p.add_argument('--source-check',type=Path,default=root/'local/cfg/object-dispatch-sources-checked-v1/checked.json');a=p.parse_args();folder,ghidra,tables,out=a.proposals,a.ghidra,a.tables,a.out;out.mkdir(parents=True,exist_ok=False)

def read(p):return json.loads(p.read_text(encoding='utf-8'))
profile=read(folder/'proposals.json');source_check=read(a.source_check);assert source_check['status']=='independent window closure comparison passed' and source_check['source_db_sha256']==profile['source_db_sha256']
raw={r['start']:{i['rva']:i for i in r['instructions']} for r in read(ghidra/'eboot.bin/ghidra.json')};independent={r['name']:r for r in read(tables/'tables.json')};checks=[]
for row in profile['proposals']:
 ins=raw[row['assignment_entry']];lea=ins[row['lea']];match=re.fullmatch(r'LEA (R\w+),\[0x([0-9a-fA-F]+)\]',lea['text']);assert match
 register=match[1];table=int(match[2],16)
 if row['adjust']:
  adjust=ins[row['adjust']];match=re.fullmatch(r'ADD '+register+r',0x([0-9a-fA-F]+)',adjust['text']);assert match;table+=int(match[1],16)
 store=ins[row['store']];assert store['text'].startswith('MOV qword ptr [') and store['text'].endswith(','+register)
 if row['object_offset']:
  displacement=re.search(r' \+ 0x([0-9a-fA-F]+)\],',store['text']);assert displacement and int(displacement[1],16)==row['object_offset']
 call=raw[row['call_entry']][row['call']];match=re.fullmatch(r'CALL qword ptr \[RAX \+ 0x([0-9a-fA-F]+)\]',call['text']);assert match
 offset=int(match[1],16);slot=table+offset;other=independent[row['name']];assert table==row['table'] and offset==row['offset'] and slot==row['slot']==other['slot']
 assert other['raw_word']==int.from_bytes(bytes.fromhex(row['slot_bytes']),'little') and other['type']==8 and other['symbol']==0 and other['addend']==row['target']==row['relocation']['addend']
 checks.append(dict(name=row['name'],independent_table=table,independent_slot=slot,independent_target=other['addend'],independent_assembly=[lea['text'],store['text'],call['text']],relocation_byte_offset=other['relocation_byte_offset']))
profile.update(status='independent object dispatch candidates passed',source_check=source_check,independent_checks=checks,proposal_sha256=sha(folder/'proposals.json'),independent_tables_sha256=sha(tables/'tables.json'),source_raw_sha256=sha(ghidra/'eboot.bin/ghidra.json'))
write_json(out/'checked.json',profile);print(json.dumps(dict(status=profile['status'],slots=len(checks),source_instructions=source_check['shared_instructions'],targets=[hex(r['independent_target']) for r in checks])),flush=True)
