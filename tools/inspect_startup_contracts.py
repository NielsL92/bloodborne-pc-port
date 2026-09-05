"""Exact supplied-libc identities for startup boundary investigations."""
import json,sqlite3,hashlib,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.formats import ElfImage
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect('file:local/cfg/startup-recovery-v2/analysis.sqlite?mode=ro',uri=True)
h,path=db.execute("SELECT hash,path FROM module WHERE name='libc.prx'").fetchone();raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
im=ElfImage(raw);dec=Cs(CS_ARCH_X86,CS_MODE_64);results=[]
for address in (0x1f560,0x5ee90,0x60510,0x60560,0x5a0,0xe0):
 row=db.execute('SELECT size FROM unwind_range WHERE module=? AND start=?',(h,address)).fetchone();size=row[0] if row else 16
 body=im.at_va(address,size)
 results.append(dict(module_sha256=h,rva=address,size=size,code_sha256=hashlib.sha256(body).hexdigest(),symbols=db.execute('SELECT nid,library,provider,name FROM symbol WHERE module=? AND rva=? AND defined=1',(h,address)).fetchall(),instructions=[dict(rva=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in dec.disasm(body,address)],import_calls=[json.loads(d) for d, in db.execute("SELECT detail FROM recovery_edge WHERE module=? AND entry=? AND kind='import_contract_unvalidated'",(h,address))]))
(out/'identities.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
