"""Recover conditional simple-leaf dependencies from a bounded initial pointer sequence."""
import argparse,json,sqlite3,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('probe',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));probe=read(a.probe/'summary.json');assert probe['fault']['reason']==27 and probe['fault']['boundary']=='unknown-compiled-target';calls=[json.loads(s) for s in (a.probe/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];last=calls[-1];pc=int(probe['fault']['pc'],16);assert last['event']=='dispatch' and last['target']==pc;assert probe['control_trace_sha256']==sha(a.probe/'native-calls.jsonl') and probe['executable_sha256']==sha(a.probe/'startup.exe')
registry=Path('local/runtime/registry-v7-memory-repeat');assert probe['registry_identity']==sha(registry/'identity.json');module=next(r for r in read(registry/'modules.json') if r['logical_base']<=pc<r['logical_base']+0x100000000);h=module['module'];base=module['logical_base'];table=last['rax'];assert base<=table<base+0x100000000 and not table%8;assert sha(module['path'])==h;im=ElfImage(Path(module['path']).read_bytes());relocs={r['offset']:r for r in im.linkage()['relocations']};known={r['pc'] for r in read(a.probe/'compilation-targets.json')+read(registry/'imports.json')};md=Cs(CS_ARCH_X86,CS_MODE_64);c=sqlite3.connect(Path('local/cfg/startup-recovery-v31-conditional-repeat/analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);slots=[];bodies=[];seen=set();matched=[]
for index in range(16):
 at=table-base+index*8;rel=relocs.get(at)
 if not rel or rel['type']!=8:break
 target=base+rel['addend'];rva=target-base;segments=[s for s in im.segments if s.type in [1,0x61000010] and s.flags&1 and s.vaddr<=rva<s.vaddr+s.filesz]
 if len(segments)!=1:break
 slot=dict(index=index,rva=at,raw_word=struct.unpack('<Q',im.at_va(at,8))[0],relocation=rel,initial_target=target,observed_requested_entry=target==pc)
 if target==pc:matched.append(index)
 if target in known:slot['status']='already compiled'
 elif target in seen:slot['status']='duplicate candidate'
 else:
  decoded=list(md.disasm(im.at_va(rva,min(16,segments[0].vaddr+segments[0].filesz-rva)),rva,count=2));first=decoded[0].bytes if decoded else b'';accepted=len(decoded)==2 and decoded[1].bytes==b'\xc3' and ((len(first)==3 and first[:2]==bytes.fromhex('8a47') and first[-1]<128) or (len(first)==4 and first[:3]==bytes.fromhex('488b47') and first[-1]<128) or (len(first)==7 and first[:3]==bytes.fromhex('488d05')))
  if not accepted:slot['status']='unsupported or non-leaf body; independent CFG recovery remains required'
  else:
   end=rva+len(first)+1;overlap=c.execute('select rva,size from recovery_instruction where module=? and rva<? and rva+size>?',(h,end,rva)).fetchall()
   if overlap:slot['status']='overlapping prior recovered instructions; disputed-boundary review required';slot['overlap']=overlap
   else:
    instructions=[dict(rva=i.address,size=i.size,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in decoded];unwind=c.execute('select start,size,confidence from unwind_range where module=? and start<? and start+size>?',(h,end,rva)).fetchall();bodies.append(dict(pc=target,rva=rva,end=end,instructions=instructions,slot_rva=at,observed_requested_entry=target==pc,unwind=unwind,evidence='Initial relocated pointer candidate plus exact bounded MOV/LEA and RET; independent Ghidra and compilation checks still required.'));slot['status']='conditional simple-leaf candidate recovered';seen.add(target)
 slots.append(slot)
assert matched and bodies and pc in {b['pc'] for b in bodies};bodies.sort(key=lambda b:b['pc']);assert len({i['rva'] for b in bodies for i in b['instructions']})==sum(len(b['instructions']) for b in bodies)
write_json(a.out/'windows.json',[dict(module=h,start=b['rva'],end=b['end']) for b in bodies]);write_json(a.out/'input.json',dict(native_memory_provenance=True,roots=[b['pc'] for b in bodies],instructions=[dict(address=base+i['rva'],bytes=i['bytes']) for b in bodies for i in b['instructions']]))
result=dict(status='conditional simple-leaf candidates recovered from bounded initial pointer sequence',module=module,base_registry_identity=probe['registry_identity'],observed_probe_sha256=sha(a.probe/'summary.json'),observed_trace_sha256=sha(a.probe/'native-calls.jsonl'),source_db_sha256=sha('local/cfg/startup-recovery-v31-conditional-repeat/analysis.sqlite'),observed_entry=pc,observed_register_table_candidate=table,matching_initial_slots=matched,slots=slots,bodies=bodies,input_sha256=sha(a.out/'input.json'),windows_sha256=sha(a.out/'windows.json'),game_execution=False,limitations=['The dispatch register supplies a candidate initial pointer sequence, not a proven vtable type, call-site instruction or complete table extent.','Only the explicitly observed entry is dynamically established. Other entries remain conditional initial-pointer dependencies even if they compile and pass synthetic tests.','The sequence is bounded to at most sixteen initial relative-pointer slots and stops at the first nonmatching slot. Its end is an analysis limit, not an object boundary.','Pointer mutation, embedded data, alternate function boundaries, unsupported bodies and unknown targets remain explicit. Nothing is removed from canonical unresolved recovery records.'])
write_json(a.out/'recovery.json',result);print(json.dumps(dict(status=result['status'],observed=hex(pc),table=hex(table),candidate_bodies=len(bodies),slots=len(slots))),flush=True)
