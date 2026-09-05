"""Merge independently checked initializer metadata and query the current startup frontier."""
import collections,hashlib,json,shutil,sqlite3,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_REG_RIP
from tools.formats import ElfImage
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
source=root/"local/cfg/startup-v1"
summary=json.loads((source/"summary.json").read_text())
check=json.loads((root/"local/cfg/ghidra-startup-v1/summary.json").read_text());assert check["status"]=="pass"
assert check["initializer_sha256"]==summary["initializer"]["sha256"]
shutil.copy2(root/"local/cfg/survey-v5/analysis.sqlite",out/"analysis.sqlite")
db=sqlite3.connect(out/"analysis.sqlite")
db.executescript("""
CREATE TABLE initializer_slot(module TEXT,ordinal INTEGER,slot INTEGER,target INTEGER,evidence TEXT,PRIMARY KEY(module,ordinal));
CREATE TABLE recovered_range(module TEXT,start INTEGER,size INTEGER,evidence TEXT,confidence TEXT,PRIMARY KEY(module,start));
""")
digest=summary["input_sha256"]
for name in (source/"summary.json",source/"roots.json",root/"local/cfg/ghidra-startup-v1/ghidra.json"):
 db.execute("INSERT INTO analysis_evidence VALUES(?,?,?)",("initializer cross-check",str(name),hashlib.sha256(name.read_bytes()).hexdigest()))
db.execute("INSERT INTO recovered_range VALUES(?,?,?,?,?)",(digest,0x20,0x71,str(source/"summary.json"),"Ghidra/Capstone recursive instruction set agrees; execution not tested"))
db.execute("INSERT OR IGNORE INTO seed VALUES(?,?,?,?)",(digest,0x20,"verified initializer entry","independent decode"))
roots=json.loads((source/"roots.json").read_text())
for r in roots:
 db.execute("INSERT INTO initializer_slot VALUES(?,?,?,?,?)",(digest,r["ordinal"],r["slot"],r["target"],r["evidence"]))
 db.execute("INSERT OR IGNORE INTO seed VALUES(?,?,?,?)",(digest,r["target"],"initial relocated constructor entry","candidate until mutation/dispatch validation"))
 db.execute("INSERT INTO decode_edge VALUES(?,?,?,?,?,?)",(digest,0x20,0x82,r["target"],"initial_constructor_target",f"slot {r['slot']:#x}; ordinal {r['ordinal']}; initial relocated state only"))
decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
instructions=json.loads((root/"local/cfg/ghidra-startup-v1/ghidra.json").read_text())["instructions"]
for row in instructions:
 ins=next(decoder.disasm(bytes.fromhex(row["bytes"]),row["rva"],count=1))
 assert ins.size==row["length"]
 db.execute("INSERT INTO instruction VALUES(?,?,?,?,?,?)",(digest,ins.address,ins.size,ins.bytes.hex(),ins.mnemonic,ins.op_str))
 db.execute("INSERT INTO ownership VALUES(?,?,?)",(digest,0x20,ins.address))
 if ins.group(CS_GRP_RET):edges=[(None,"terminal","ret")]
 elif ins.group(CS_GRP_JUMP):
  edges=[(ins.operands[0].imm,"direct_jump",ins.op_str)]
  if ins.mnemonic!="jmp":edges.append((ins.address+ins.size,"fallthrough",""))
 else:
  edges=[(ins.address+ins.size,"fallthrough","")]
  if ins.group(CS_GRP_CALL):edges.append((None,"unresolved_indirect_call","initial table state known; mutable/runtime targets unvalidated"))
 for target,kind,detail in edges:
  db.execute("INSERT INTO decode_edge VALUES(?,?,?,?,?,?)",(digest,0x20,ins.address,target,kind,detail))
db.execute("INSERT INTO decoded_range VALUES(?,?,?,?,?,?,?,?)",(digest,0x20,0x71,len(instructions),sum(i["length"] for i in instructions),2,0,0))
db.commit()
# Query only evidence already present: stop at missing ranges and unresolved services/targets.
# A known start with decoded instructions is still not a complete function.
images={};links={};relocs={};symbol_names={x["nid"]:x.get("resolved_name") for x in json.loads((root/"local/analysis/imports.json").read_text())}
for h,path in db.execute("SELECT hash,path FROM module"):
 raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
 images[h]=ElfImage(raw);links[h]=images[h].linkage();relocs[h]={r["offset"]:r for r in links[h]["relocations"]}
def imported(h,target):
 try:i=next(decoder.disasm(images[h].at_va(target,15),target,count=1),None)
 except Exception:return None
 if not i or i.mnemonic!="jmp" or i.operands[0].type!=X86_OP_MEM or i.operands[0].mem.base!=X86_REG_RIP:return None
 r=relocs[h].get(target+i.size+i.operands[0].mem.disp)
 if not r or r["type"]!=7:return None
 s=links[h]["symbols"][r["symbol"]]
 return dict(s,resolved_name=symbol_names.get(s["nid"]))
queue=collections.deque([(digest,0xa0)]);seen=set();frontier=[];traversed=[]
follow_kinds={"direct_call","cross_range_jump","initial_constructor_target"}
while queue:
 h,address=queue.popleft()
 if (h,address) in seen:continue
 seen.add((h,address))
 decoded=db.execute("SELECT instructions,issues FROM decoded_range WHERE module=? AND start=?",(h,address)).fetchone()
 if not decoded:
  frontier.append(dict(module=h,target=address,kind="entry_not_decoded",indexed_range=bool(db.execute("SELECT 1 FROM unwind_range WHERE module=? AND start=?",(h,address)).fetchone())))
  continue
 traversed.append(dict(module=h,start=address,instructions=decoded[0],decode_issues=decoded[1]))
 for caller,target,kind,detail in db.execute("SELECT source,target,kind,detail FROM decode_edge WHERE module=? AND range_start=? AND kind!='fallthrough'",(h,address)).fetchall():
  if kind.startswith("unresolved") or kind=="service_or_trap_boundary":
   frontier.append(dict(module=h,owner=address,caller=caller,target=target,kind=kind,detail=detail))
  elif kind in follow_kinds:
   imp=imported(h,target)
   if imp is not None:
    candidates=[dict(module=other,rva=s["value"]) for other,link in links.items() for s in link["symbols"] if s["defined"] and (s["nid"],s["library"],s["module"])==(imp["nid"],imp["library"],imp["module"])]
    frontier.append(dict(module=h,owner=address,caller=caller,target=target,kind="import_contract_unvalidated",symbol=imp,bundled_candidates=candidates))
    for candidate in candidates:queue.append((candidate["module"],candidate["rva"]))
   else:queue.append((h,target))
  elif kind.endswith("_call"):
   frontier.append(dict(module=h,owner=address,caller=caller,target=target,kind="annotated_control_contract_requires_runtime",contract_kind=kind))
 for rva,kind,detail in db.execute("SELECT rva,kind,detail FROM decode_issue WHERE module=? AND range_start=?",(h,address)):
  frontier.append(dict(module=h,owner=address,caller=rva,kind="decode_"+kind,detail=detail))
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
db.close()
counts=collections.Counter(x["kind"] for x in frontier)
report=dict(status="P3 startup compilation/exit closure gate NOT passed",constructor_roots=len(roots),constructor_unindexed_roots=summary["reverse_array"]["unindexed_roots"],decoded_ranges_traversed=len(traversed),frontier_counts=dict(counts),
 db_sha256=hashlib.sha256((out/"analysis.sqlite").read_bytes()).hexdigest(),limitations="Only the currently recovered ranges are traversed. Missing bodies stop expansion; constructor targets reflect initial relocated data. Traversal is not execution or proof of complete startup discovery.")
for name,value in (("summary.json",report),("frontier.json",frontier),("traversed.json",traversed)):
 (out/name).write_bytes((json.dumps(value,indent=2)+"\n").encode())
print(json.dumps(report),flush=True)
