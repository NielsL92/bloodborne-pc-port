"""Extract exception-entry metadata from all eight modules into a fresh database."""
import collections,hashlib,json,shutil,sqlite3,sys,time
from pathlib import Path
from tools.formats import ElfImage
from tools.exception_metadata import fde_metadata,lsda_metadata
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
shutil.copy2(root/"local/cfg/seed-v1/analysis.sqlite",out/"analysis.sqlite")
db=sqlite3.connect(out/"analysis.sqlite")
db.executescript("""
CREATE TABLE exception_region(module TEXT,start INTEGER,size INTEGER,fde INTEGER,cie INTEGER,lsda INTEGER,personality_slot INTEGER,evidence TEXT,PRIMARY KEY(module,start));
CREATE TABLE exception_call_site(module TEXT,range_start INTEGER,record_rva INTEGER,start INTEGER,size INTEGER,landing_pad INTEGER,action INTEGER);
CREATE TABLE exception_action(module TEXT,range_start INTEGER,rva INTEGER,type_filter INTEGER,next_rva INTEGER);
CREATE TABLE exception_issue(module TEXT,range_start INTEGER,detail TEXT);
""")
all_regions=[];module_summaries=[];begin=time.perf_counter()
for digest,path,name in db.execute("SELECT hash,path,name FROM module ORDER BY name").fetchall():
 raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
 im=ElfImage(raw);cache={};augments=collections.Counter();count=0
 for start,size,fde in db.execute("SELECT start,size,fde FROM unwind_range WHERE module=? ORDER BY start",(digest,)).fetchall():
  try:
   meta=fde_metadata(im,dict(start=start,size=size,fde=fde),cache)
   augments[meta["augmentation"]]+=1
   if meta["lsda"] is None:continue
   parsed=lsda_metadata(im,meta)
  except Exception as e:
   db.execute("INSERT INTO exception_issue VALUES(?,?,?)",(digest,start,f"{type(e).__name__}: {e}"))
   continue
  region=dict(module=digest,name=name,**(meta|parsed));all_regions.append(region);count+=1
  db.execute("INSERT INTO exception_region VALUES(?,?,?,?,?,?,?,?)",(digest,start,size,fde,meta["cie"],meta["lsda"],meta["personality_slot"],json.dumps(region,sort_keys=True)))
  for c in parsed["call_sites"]:
   db.execute("INSERT INTO exception_call_site VALUES(?,?,?,?,?,?,?)",(digest,start,c["record_rva"],c["start"],c["length"],c["landing_pad"],c["action"]))
   if c["landing_pad"] is not None:
    db.execute("INSERT OR IGNORE INTO seed VALUES(?,?,?,?)",(digest,c["landing_pad"],"LSDA landing pad","static metadata; not executed"))
  for a in parsed["actions"]:
   db.execute("INSERT INTO exception_action VALUES(?,?,?,?,?)",(digest,start,a["rva"],a["type_filter"],a["next_rva"]))
 row=dict(module=digest,name=name,augmentations=dict(augments),lsda_regions=count)
 module_summaries.append(row);print(json.dumps(row),flush=True)
db.commit();assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
counts={t:db.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("exception_region","exception_call_site","exception_action","exception_issue")}
landings=db.execute("SELECT count(*) FROM (SELECT DISTINCT module,landing_pad FROM exception_call_site WHERE landing_pad IS NOT NULL)").fetchone()[0]
issues=[dict(module=m,start=s,detail=d) for m,s,d in db.execute("SELECT * FROM exception_issue")]
db.close()
report=dict(status="static exception metadata extracted; runtime exception gate NOT passed",counts=counts,unique_landing_pads=landings,modules=module_summaries,issues=issues,seconds=time.perf_counter()-begin,db_sha256=hashlib.sha256((out/"analysis.sqlite").read_bytes()).hexdigest(),limitation="CFI is not interpreted into a Windows unwind implementation. Type matching, dynamic personalities, saved register rules and landing-pad execution are not validated.")
(out/"regions.json").write_bytes((json.dumps(all_regions,indent=2)+"\n").encode())
(out/"summary.json").write_bytes((json.dumps(report,indent=2)+"\n").encode())
print(json.dumps(report),flush=True)
if issues:raise SystemExit(2)
