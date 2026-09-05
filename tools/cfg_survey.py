"""Bounded recursive CFG survey with explicit unresolved edges and instruction-overlap checks."""
import argparse,collections,hashlib,json,random,shutil,sqlite3,sys,time
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_REG_RIP
from tools.formats import ElfImage
parser=argparse.ArgumentParser()
parser.add_argument("out")
parser.add_argument("--exceptions",action="store_true",help="Include all independently checked exception ranges and landing-pad entries")
args=parser.parse_args()
root=Path.cwd();out=root/args.out;out.mkdir(parents=True,exist_ok=False)
source=root/("local/cfg/exceptions-v2/analysis.sqlite" if args.exceptions else "local/cfg/seed-v1/analysis.sqlite")
if args.exceptions:
 verification=json.loads((root/"local/cfg/ghidra-exceptions-v2/summary.json").read_text())
 assert verification["status"]=="pass"
shutil.copy2(source,out/"analysis.sqlite")
db=sqlite3.connect(out/"analysis.sqlite")
db.executescript("""
CREATE TABLE analysis_evidence(kind TEXT,path TEXT,sha256 TEXT);
CREATE TABLE instruction(module TEXT,rva INTEGER,size INTEGER,bytes TEXT,mnemonic TEXT,operands TEXT,PRIMARY KEY(module,rva));
CREATE TABLE ownership(module TEXT,range_start INTEGER,instruction INTEGER,PRIMARY KEY(module,range_start,instruction));
CREATE TABLE decode_edge(module TEXT,range_start INTEGER,source INTEGER,target INTEGER,kind TEXT,detail TEXT);
CREATE INDEX decoded_edge_source ON decode_edge(module,source);
CREATE TABLE rip_reference(module TEXT,range_start INTEGER,instruction INTEGER,target INTEGER,operation TEXT);
CREATE TABLE decode_issue(module TEXT,range_start INTEGER,rva INTEGER,kind TEXT,detail TEXT);
CREATE TABLE decoded_range(module TEXT,start INTEGER,size INTEGER,instructions INTEGER,decoded_bytes INTEGER,unresolved_indirect INTEGER,cross_range INTEGER,issues INTEGER,PRIMARY KEY(module,start));
""")
def evidence(kind,path):
 path=root/path
 db.execute("INSERT INTO analysis_evidence VALUES(?,?,?)",(kind,str(path),hashlib.sha256(path.read_bytes()).hexdigest()))
evidence("source metadata database",source)
evidence("import control contracts","tools/cfg_import_contracts.json")
evidence("independent switch check","local/cfg/ghidra-bitreader-v1/ghidra.json")
if args.exceptions:
 evidence("independent exception check","local/cfg/ghidra-exceptions-v2/summary.json")
 for name in ("eboot.bin","libc.prx"):
  evidence("independent exception rows",f"local/cfg/ghidra-exceptions-v2/{name}/ghidra.json")
decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
rng=random.Random(0x50303);selection=[];summaries=[];begin=time.perf_counter()
candidates=json.loads((root/"local/compiler-spike/candidates.json").read_text())
main_starts={x["start"] for x in candidates["scaling_batch"]}
main_starts.update([0x3360,0x1a50,0x3500,0x3530,0x2550,0x65d0,0xb820,0x2fa30,0x3df50,0x3240,0x5e4e0,0x77e80,0x2b2b0,0x401f0])
import_records=[]
annotation=json.loads((root/"tools/cfg_import_contracts.json").read_text())
assert annotation["schema"]==2
contracts={(a["nid"],a["library"],a["module"]):a for a in annotation["contracts"]}
assert len(contracts)==len(annotation["contracts"])
# Enforce byte identity of supplied-module implementation evidence before using it.
for contract in contracts.values():
 for evidence in [e for e in contract["evidence"] if e["kind"]=="supplied module static implementation"]+contract.get("local_entries",[]):
  if "module_sha256" in evidence:
   row=db.execute("SELECT path FROM module WHERE hash=?",(evidence["module_sha256"],)).fetchone()
   assert row, "annotation module missing from database"
   evidence_raw=Path(row[0]).read_bytes()
   assert hashlib.sha256(evidence_raw).hexdigest()==evidence["module_sha256"]
   evidence_body=ElfImage(evidence_raw).at_va(evidence["rva"],evidence["size"])
   assert hashlib.sha256(evidence_body).hexdigest()==evidence["code_sha256"]
done=0
for module_hash,path,name,entry in db.execute("SELECT hash,path,name,entry FROM module ORDER BY name").fetchall():
 raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==module_hash
 image=ElfImage(raw)
 linkage=image.linkage();relocations={r["offset"]:r for r in linkage["relocations"]}
 contract_cache={}
 local_contracts={e["rva"]:c for c in contracts.values() for e in c.get("local_entries",[]) if e["module_sha256"]==module_hash}
 def import_contract(target):
  if target in local_contracts:
   contract=local_contracts[target]
   if target not in contract_cache:
    import_records.append(dict(module=module_hash,entry=target,contract_id=contract["id"],annotation="tools/cfg_import_contracts.json",match="exact local hash/RVA/bytes"))
    contract_cache[target]=contract
   return contract
  if target in contract_cache:return contract_cache[target]
  contract_cache[target]=None
  try:ins=next(decoder.disasm(image.at_va(target,15),target,count=1),None)
  except Exception:return None
  if not ins or ins.mnemonic!="jmp" or ins.operands[0].type!=X86_OP_MEM:return None
  op=ins.operands[0]
  if op.mem.base!=X86_REG_RIP:return None
  got=target+ins.size+op.mem.disp
  relocation=relocations.get(got)
  if not relocation or relocation["type"]!=7:return None
  symbol=linkage["symbols"][relocation["symbol"]]
  contract=contracts.get(tuple(symbol[k] for k in ("nid","library","module")))
  if contract is None:return None
  contract_cache[target]=contract
  import_records.append(dict(module=module_hash,stub=target,got=got,symbol=symbol,contract_id=contract["id"],annotation="tools/cfg_import_contracts.json"))
  return contract
 ranges=[dict(start=a,size=b) for a,b in db.execute("SELECT start,size FROM unwind_range WHERE module=? ORDER BY start",(module_hash,))]
 if name=="eboot.bin":chosen=[f for f in ranges if f["start"] in main_starts or f["start"]==entry]
 else:
  # Eight samples from each size quartile, deterministic; very small modules use all ranges.
  ordered=sorted(ranges,key=lambda x:(x["size"],x["start"]));chosen=[]
  for quartile in range(4):
   pool=ordered[len(ordered)*quartile//4:len(ordered)*(quartile+1)//4]
   chosen+=rng.sample(pool,min(8,len(pool)))
 landing_seeds=collections.defaultdict(set)
 if args.exceptions:
  extra={r[0] for r in db.execute("SELECT start FROM exception_region WHERE module=?",(module_hash,))}
  chosen=list({r["start"]:r for r in chosen+[r for r in ranges if r["start"] in extra]}.values())
  for owner,pad in db.execute("SELECT range_start,landing_pad FROM exception_call_site WHERE module=? AND landing_pad IS NOT NULL",(module_hash,)):
   landing_seeds[owner].add(pad)
 chosen.sort(key=lambda x:x["start"])
 known=collections.defaultdict(list)
 for source,target in db.execute("SELECT source,target FROM edge WHERE module=?",(module_hash,)):known[source].append(target)
 for fn in chosen:
  start,size=fn["start"],fn["size"];end=start+size
  selection.append(dict(module=module_hash,name=name,start=start,size=size))
  instructions={};owners={};queue=collections.deque([start]+sorted(landing_seeds[start]));issues=[];edges=[];refs=[];unknown=0;outside=0
  try:body=image.at_va(start,size)
  except Exception as e:
   body=b"";issues.append((start,"unreadable_range",str(e)));queue.clear()
  def add(target,source,kind):
   edges.append((source,target,kind,"decoded direct target"))
   if start<=target<end:queue.append(target)
  while queue:
   address=queue.popleft()
   if address in instructions:continue
   if not start<=address<end:continue
   if address in owners:
    issues.append((address,"overlapping_decode_target",f"target inside instruction {owners[address]:x}"));continue
   offset=address-start
   ins=next(decoder.disasm(body[offset:offset+15],address,count=1),None)
   if ins is None or address+ins.size>end:
    issues.append((address,"undecodable_or_crosses_range_end",body[offset:offset+15].hex()));continue
   conflict=[x for x in range(address,address+ins.size) if x in owners]
   if conflict:
    issues.append((address,"overlapping_decode_bytes",json.dumps(conflict)));continue
   instructions[address]=ins
   for x in range(address,address+ins.size):owners[x]=address
   for op in ins.operands:
    if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
     refs.append((address,address+ins.size+op.mem.disp,ins.mnemonic))
   next_address=address+ins.size
   if ins.group(CS_GRP_RET) or ins.mnemonic in ("iret","iretq","sysret","sysretq","ud2","hlt"):
    edges.append((address,None,"terminal",ins.mnemonic));continue
   if ins.mnemonic in ("syscall","int","int3"):
    edges.append((address,None,"service_or_trap_boundary",ins.mnemonic))
   if ins.group(CS_GRP_CALL):
    target=ins.operands[0].imm if ins.operands[0].type==X86_OP_IMM else None
    contract=import_contract(target) if target is not None else None
    edges.append((address,target,contract["edge_kind"] if contract else "direct_call" if target is not None else "unresolved_indirect_call",ins.op_str))
    if contract:
     if contract["restored_target_unknown"]:
      unknown+=1
      edges.append((address,None,contract.get("unknown_exit_kind","unresolved_restored_context"),contract["id"]))
     continue
    if target is None:unknown+=1
   elif ins.group(CS_GRP_JUMP):
    if ins.operands[0].type==X86_OP_IMM:
     target=ins.operands[0].imm
     if not start<=target<end:outside+=1
     add(target,address,"direct_jump" if start<=target<end else "cross_range_jump")
    elif address in known:
     for target in known[address]:add(target,address,"validated_jump_table")
    else:
     unknown+=1;edges.append((address,None,"unresolved_indirect_jump",ins.op_str))
    if ins.mnemonic in ("jmp","ljmp"):continue
   if next_address<end:
    edges.append((address,next_address,"fallthrough",""));queue.append(next_address)
   else:
    issues.append((address,"fallthrough_at_range_end",ins.mnemonic))
  for address,ins in sorted(instructions.items()):
   previous=db.execute("SELECT bytes FROM instruction WHERE module=? AND rva=?",(module_hash,address)).fetchone()
   if previous and previous[0]!=ins.bytes.hex():raise RuntimeError("cross-owner byte mismatch")
   db.execute("INSERT OR IGNORE INTO instruction VALUES(?,?,?,?,?,?)",(module_hash,address,ins.size,ins.bytes.hex(),ins.mnemonic,ins.op_str))
   db.execute("INSERT INTO ownership VALUES(?,?,?)",(module_hash,start,address))
  db.executemany("INSERT INTO decode_edge VALUES(?,?,?,?,?,?)",[(module_hash,start,*e) for e in edges])
  db.executemany("INSERT INTO rip_reference VALUES(?,?,?,?,?)",[(module_hash,start,*r) for r in refs])
  db.executemany("INSERT INTO decode_issue VALUES(?,?,?,?,?)",[(module_hash,start,*i) for i in issues])
  db.execute("INSERT INTO decoded_range VALUES(?,?,?,?,?,?,?,?)",(module_hash,start,size,len(instructions),len(owners),unknown,outside,len(issues)))
  summaries.append(dict(module=module_hash,start=start,size=size,instructions=len(instructions),decoded_bytes=len(owners),unresolved_indirect=unknown,cross_range_jumps=outside,issues=len(issues)))
  done+=1
  if done%100==0:db.commit();print(json.dumps(dict(decoded_ranges=done,elapsed_seconds=time.perf_counter()-begin)),flush=True)
db.commit()
# Independent Ghidra comparison for the validated real switch, now against recursive reachability.
main_hash=candidates["input_sha256"]
g=json.loads((root/"local/cfg/ghidra-bitreader-v1/ghidra.json").read_text())
rows=db.execute("SELECT i.rva,i.size,i.bytes FROM instruction i JOIN ownership o ON i.module=o.module AND i.rva=o.instruction WHERE o.module=? AND o.range_start=?",(main_hash,0x401f0)).fetchall()
actual={rva:(length,b) for rva,length,b in rows};expected={x["rva"]:(x["length"],x["bytes"]) for x in g["instructions"]}
assert actual==expected,dict(only_recursive=sorted(set(actual)-set(expected)),only_ghidra=sorted(set(expected)-set(actual)))
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
counts={name:db.execute(f"SELECT count(*) FROM {name}").fetchone()[0] for name in ("decoded_range","instruction","ownership","decode_edge","rip_reference","decode_issue","analysis_evidence")}
kinds=dict(db.execute("SELECT kind,count(*) FROM decode_issue GROUP BY kind").fetchall())
edge_kinds=dict(db.execute("SELECT kind,count(*) FROM decode_edge GROUP BY kind").fetchall())
db.close()
report=dict(status="bounded survey completed; P3 startup/control-flow closure gate NOT passed",
 counts=counts,issue_kinds=kinds,edge_kinds=edge_kinds,import_contracts=import_records,elapsed_seconds=time.perf_counter()-begin,
 independent_switch_instruction_set_equal=True,selection_seed="0x50303",exception_entries_included=args.exceptions,
 limitations="Selected metadata ranges only. Calls are boundaries, not executed or recursively expanded here. Unknown indirect targets, cross-range targets and decode conflicts are preserved; undecoded bytes can be data or unrecovered code.")
(out/"selection.json").write_bytes((json.dumps(selection,indent=2)+"\n").encode())
(out/"ranges.json").write_bytes((json.dumps(summaries,indent=2)+"\n").encode())
(out/"summary.json").write_bytes((json.dumps(report,indent=2)+"\n").encode())
print(json.dumps(report),flush=True)
