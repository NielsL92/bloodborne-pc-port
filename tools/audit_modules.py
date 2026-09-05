"""Inventory transitive bundled-module imports; candidate matching is not implementation."""
import hashlib
import json
from pathlib import Path
from tools.formats import ElfImage
from tools.analyze import nid_index
ROOT=Path(__file__).resolve().parents[1]
names,hle=nid_index(ROOT/"external/shadPS4")
files=[ROOT/"local/update/uroot/eboot.bin",*sorted((ROOT/"local/base-code/uroot/sce_module").glob("*.prx"))]
parsed={}
exports={}
for f in files:
    raw=f.read_bytes()
    links=ElfImage(raw).linkage()
    parsed[f.name]=(f,raw,links)
    for s in links["symbols"]:
        if s["name"] and s["defined"]:
            exports.setdefault((s["nid"],s["library"]),[]).append(f.name)
modules=[]
for name,(f,raw,links) in parsed.items():
    imports=[]
    for s in links["symbols"]:
        if not s["name"] or s["defined"]:
            continue
        k=(s["nid"],s["library"])
        imports.append(dict(symbol=s,name=names.get(s["nid"]),hle_registration=k in hle,bundled_candidates=exports.get(k,[])))
    unresolved=[s for s in imports if not s["hle_registration"] and not s["bundled_candidates"]]
    modules.append(dict(file=str(f),sha256=hashlib.sha256(raw).hexdigest(),needed=links["needed"],
                        imports=imports,imports_without_candidates=unresolved))
out=ROOT/"local/analysis/transitive-modules.json"
out.write_text(json.dumps(dict(caveat="Static candidates only: no ABI, semantics, runtime-loading, or version validation.",modules=modules),indent=2)+"\n")
summary=[dict(module=Path(m["file"]).name,imports=len(m["imports"]),without_candidates=len(m["imports_without_candidates"]),
              missing=[i["name"] or i["symbol"]["name"] for i in m["imports_without_candidates"]]) for m in modules]
(ROOT/"reports/module-audit.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
