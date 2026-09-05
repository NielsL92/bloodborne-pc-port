"""Create a versioned metadata/provenance database; metadata ranges are not proven functions."""
import collections,hashlib,json,sqlite3,sys,time
from pathlib import Path
from tools.formats import ElfImage
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect(out/"analysis.sqlite")
db.executescript("""
PRAGMA foreign_keys=ON;
CREATE TABLE module(hash TEXT PRIMARY KEY,path TEXT NOT NULL,name TEXT NOT NULL,bytes INTEGER,entry INTEGER,kind TEXT);
CREATE TABLE segment(module TEXT REFERENCES module(hash),ordinal INTEGER,type INTEGER,flags INTEGER,rva INTEGER,file_offset INTEGER,file_size INTEGER,memory_size INTEGER,alignment INTEGER,PRIMARY KEY(module,ordinal));
CREATE TABLE unwind_range(id INTEGER PRIMARY KEY,module TEXT REFERENCES module(hash),start INTEGER,size INTEGER,fde INTEGER,evidence TEXT,confidence TEXT);
CREATE INDEX unwind_address ON unwind_range(module,start);
CREATE TABLE symbol(module TEXT REFERENCES module(hash),ordinal INTEGER,name TEXT,nid TEXT,bind INTEGER,type INTEGER,defined INTEGER,rva INTEGER,size INTEGER,library TEXT,provider TEXT,PRIMARY KEY(module,ordinal));
CREATE TABLE relocation(module TEXT REFERENCES module(hash),location INTEGER,type INTEGER,symbol INTEGER,addend INTEGER,table_kind TEXT);
CREATE INDEX relocation_address ON relocation(module,location);
CREATE TABLE required_name(module TEXT REFERENCES module(hash),name TEXT);
CREATE TABLE seed(module TEXT REFERENCES module(hash),rva INTEGER,reason TEXT,confidence TEXT,PRIMARY KEY(module,rva,reason));
CREATE TABLE pointer_candidate(module TEXT REFERENCES module(hash),location INTEGER,target INTEGER,evidence TEXT,confidence TEXT);
CREATE TABLE issue(module TEXT REFERENCES module(hash),kind TEXT,detail TEXT);
CREATE TABLE validated_contract(module TEXT REFERENCES module(hash),rva INTEGER,name TEXT,evidence_path TEXT,evidence_sha256 TEXT);
CREATE TABLE edge(module TEXT REFERENCES module(hash),source INTEGER,target INTEGER,kind TEXT,evidence TEXT,confidence TEXT);
""")
def sha(b):return hashlib.sha256(b).hexdigest()
modules=json.loads((root/"local/analysis/transitive-modules.json").read_text())["modules"]
summary=[];start=time.perf_counter()
for item in modules:
 path=Path(item["file"]);raw=path.read_bytes();digest=sha(raw);assert digest==item["sha256"]
 im=ElfImage(raw);link=im.linkage()
 db.execute("INSERT INTO module VALUES(?,?,?,?,?,?)",(digest,str(path),path.name,len(raw),im.entry,"SELF" if im.is_self else "ELF"))
 for n,s in enumerate(im.segments):
  db.execute("INSERT INTO segment VALUES(?,?,?,?,?,?,?,?,?)",(digest,n,s.type,s.flags,s.vaddr,s.offset,s.filesz,s.memsz,s.align))
 def executable(addr):return any(s.type in (1,0x61000010) and s.flags&1 and s.vaddr<=addr<s.vaddr+s.memsz for s in im.segments)
 def seed(addr,reason,confidence):
  if executable(addr):db.execute("INSERT OR IGNORE INTO seed VALUES(?,?,?,?)",(digest,addr,reason,confidence))
 seed(im.entry,"ELF entry","metadata")
 ranges=[];error=None
 try:ranges=im.unwind_functions()
 except Exception as e:error=f"{type(e).__name__}: {e}";db.execute("INSERT INTO issue VALUES(?,?,?)",(digest,"unsupported_unwind",error))
 for f in ranges:
  db.execute("INSERT INTO unwind_range(module,start,size,fde,evidence,confidence) VALUES(?,?,?,?,?,?)",(digest,f["start"],f["size"],f.get("fde"),json.dumps(f,sort_keys=True),"metadata range; not proven function"))
  seed(f["start"],"EH frame start","metadata")
 ordered=sorted(ranges,key=lambda f:f["start"]);max_end=0
 for f in ordered:
  if f["start"]<max_end:db.execute("INSERT INTO issue VALUES(?,?,?)",(digest,"overlapping_unwind_range",json.dumps(f)))
  max_end=max(max_end,f["start"]+f["size"])
 for s in link["symbols"]:
  db.execute("INSERT INTO symbol VALUES(?,?,?,?,?,?,?,?,?,?,?)",(digest,s["index"],s["name"],s["nid"],s["bind"],s["type"],s["defined"],s["value"],s["size"],s["library"],s["module"]))
  if s["defined"] and s["type"]==2:seed(s["value"],"defined function symbol","metadata")
 for r in link["relocations"]:
  db.execute("INSERT INTO relocation VALUES(?,?,?,?,?,?)",(digest,r["offset"],r["type"],r["symbol"],r["addend"],r["table"]))
  if r["type"]==8 and executable(r["addend"]):
   db.execute("INSERT INTO pointer_candidate VALUES(?,?,?,?,?)",(digest,r["offset"],r["addend"],"R_X86_64_RELATIVE addend in executable mapping","candidate; may be interior address/data"))
 for name in link["needed"]:db.execute("INSERT INTO required_name VALUES(?,?)",(digest,name))
 for tag,val in im.dynamic():
  if tag==12:seed(val,"DT_INIT","metadata")
 row=dict(file=path.name,sha256=digest,unwind_ranges=len(ranges),unwind_error=error,symbols=len(link["symbols"]),relocations=len(link["relocations"]))
 summary.append(row);print(json.dumps(row),flush=True)
digest="d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9"
recovery_path=root/"local/compiler-spike/real-jump-v1/recovery.json"
rec=json.loads(recovery_path.read_text())
for target in rec["targets"]:
 db.execute("INSERT OR IGNORE INTO seed VALUES(?,?,?,?)",(digest,target,"verified relative jump-table entry","P2 contract"))
 db.execute("INSERT INTO edge VALUES(?,?,?,?,?,?)",(digest,0x4023a,target,"indirect jump",str(recovery_path),"five targets exercised by differential test"))
db.execute("INSERT INTO validated_contract VALUES(?,?,?,?,?)",(digest,0x401f0,"bit-reader: 2112 full-state cases and independent bitstream",str(recovery_path),sha(recovery_path.read_bytes())))
counts={name:db.execute(f"SELECT count(*) FROM {name}").fetchone()[0] for name in ("module","segment","unwind_range","symbol","relocation","required_name","seed","pointer_candidate","issue","edge","validated_contract")}
db.commit()
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
assert not db.execute("PRAGMA foreign_key_check").fetchall()
db.close()
report=dict(status="metadata database built; P3 recovery gate NOT passed",modules=summary,counts=counts,seconds=time.perf_counter()-start,db_sha256=sha((out/"analysis.sqlite").read_bytes()),
 limitations="No metadata range is automatically a complete function. Pointer candidates are not confirmed call targets. No broad CFG decode, startup closure, dynamic module closure, or execution coverage is claimed.")
(out/"summary.json").write_bytes((json.dumps(report,indent=2)+"\n").encode())
print(json.dumps(report),flush=True)
