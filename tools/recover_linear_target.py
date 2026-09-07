"""Recover one observed missing target through a bounded straight-line return."""
import argparse,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET,CS_GRP_INT,CS_GRP_IRET
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('probe',type=Path);p.add_argument('source',type=Path);p.add_argument('registry',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
probe=read(a.probe/'summary.json');fault=probe['fault'];assert probe['game_aot_execution'] and not probe['original_byte_cpu_execution'];assert fault['boundary']=='unknown-compiled-target' and fault['reason']==27
pc=int(fault['pc'],16);events=[json.loads(s) for s in (a.probe/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];assert events[-1]['event']=='dispatch' and events[-1]['target']==pc
assert probe['control_trace_sha256']==sha(a.probe/'native-calls.jsonl');assert probe['executable_sha256']==sha(a.probe/'startup.exe');assert probe['registry_identity']==sha(a.registry/'identity.json')
assert pc not in {r['pc'] for r in read(a.registry/'targets.json')+read(a.registry/'imports.json')}
modules=read(a.registry/'modules.json');selected=[r for r in modules if r['logical_base']<=pc<r['logical_base']+0x100000000];assert len(selected)==1;module=selected[0];h=module['module'];rva=pc-module['logical_base'];assert sha(module['path'])==h
image=ElfImage(Path(module['path']).read_bytes());segments=[s for s in image.segments if s.type in (1,0x61000010) and s.flags&1 and s.vaddr<=rva<s.vaddr+s.filesz];assert len(segments)==1;segment=segments[0];raw=image.at_va(rva,min(256,segment.vaddr+segment.filesz-rva))
decode=Cs(CS_ARCH_X86,CS_MODE_64);decode.detail=True;instructions=[];offset=0
for ins in decode.disasm(raw,rva):
 assert ins.address==rva+offset and not any(ins.group(g) for g in [CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_INT,CS_GRP_IRET]),'nonlinear target requires full CFG recovery'
 assert ins.mnemonic not in ['syscall','sysenter','ud2','hlt','int3'],'special control requires separate recovery'
 instructions.append(dict(rva=ins.address,size=ins.size,bytes=ins.bytes.hex(),mnemonic=ins.mnemonic,operands=ins.op_str));offset+=ins.size
 if ins.group(CS_GRP_RET):
  assert ins.bytes==b'\xc3','nonordinary return requires separate contract'
  break
else:raise AssertionError('no bounded ordinary return')
assert offset<=256
c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
assert c.execute('select path from module where hash=?',(h,)).fetchone()
existing=c.execute('select rva,size,bytes from recovery_instruction where module=? and rva<? and rva+size>?',(h,rva+offset,rva)).fetchall()
assert not existing,'overlapping recovered body needs disputed-boundary review'
unwind=c.execute('select start,size,evidence,confidence from unwind_range where module=? and start<? and start+size>?',(h,rva+offset,rva)).fetchall()
seeds=c.execute('select reason,confidence from seed where module=? and rva=?',(h,rva)).fetchall()
pointers=c.execute('select location,evidence,confidence from pointer_candidate where module=? and target=?',(h,rva)).fetchall();c.close()
write_json(a.out/'windows.json',[dict(module=h,start=rva,end=rva+offset)])
write_json(a.out/'input.json',dict(native_memory_provenance=True,roots=[pc],instructions=[dict(address=module['logical_base']+i['rva'],bytes=i['bytes']) for i in instructions]))
result=dict(status='bounded target body recovered pending independent Ghidra and AOT validation',module=module,pc=pc,rva=rva,end=rva+offset,instructions=instructions,source_db_sha256=sha(a.source/'analysis.sqlite'),base_registry_identity=sha(a.registry/'identity.json'),observed_probe_sha256=sha(a.probe/'summary.json'),observed_trace_sha256=sha(a.probe/'native-calls.jsonl'),last_dispatch=events[-1],overlapping_unwind=unwind,seed_evidence=seeds,pointer_candidates=pointers,input_sha256=sha(a.out/'input.json'),windows_sha256=sha(a.out/'windows.json'),game_execution=False,limitations=['The observed native target establishes one entry request, not the dynamic caller instruction or general execution coverage.','Body extent ends at the first decoded ordinary RET under a bounded linear model; independent decoding and compiled semantic checks are required.','Unwind ranges and pointer candidates are retained evidence, not function or mutability proofs.','Other roots, data/code ambiguities, table mutation and unknown targets remain open. No following padding or adjacent entry is included.'])
write_json(a.out/'recovery.json',result);print(json.dumps(dict(status=result['status'],pc=hex(pc),instructions=len(instructions),bytes=offset,unwind=unwind,pointer_candidates=len(pointers))),flush=True)
