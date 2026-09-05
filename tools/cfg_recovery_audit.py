"""Inspect recovered startup frontiers without modifying their databases."""
import collections,json,sqlite3,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.formats import ElfImage
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect(f'{(source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
issues=db.execute('SELECT module,entry,rva,kind,detail FROM recovery_issue ORDER BY module,entry,rva').fetchall()
counts=dict(collections.Counter(r[3] for r in issues));examples=[];seen=collections.Counter();images={}
for h,path in db.execute('SELECT hash,path FROM module'):images[h]=ElfImage(Path(path).read_bytes())
dec=Cs(CS_ARCH_X86,CS_MODE_64)
for h,entry,rva,kind,detail in issues:
 if seen[kind]>=12:continue
 seen[kind]+=1
 try:ins=[dict(rva=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in dec.disasm(images[h].at_va(max(entry,rva-24),64),max(entry,rva-24))]
 except Exception:ins=[]
 previous=db.execute('SELECT i.rva,i.mnemonic,i.operands FROM recovery_instruction i JOIN recovery_owner o ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=? AND i.rva<=? ORDER BY i.rva DESC LIMIT 8',(h,entry,rva)).fetchall()
 examples.append(dict(module=h,entry=entry,rva=rva,kind=kind,detail=detail,preceding_recovered=list(reversed(previous)),linear_context_not_coverage=ins))
report=dict(issue_counts=counts,examples=examples,exception_regions_requested=db.execute("SELECT count(*) FROM recovery_edge WHERE kind='exception_runtime_unvalidated'").fetchone()[0],module_counts=dict(db.execute('SELECT m.name,count(*) FROM recovery_entry r JOIN module m ON m.hash=r.module GROUP BY m.name')))
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
