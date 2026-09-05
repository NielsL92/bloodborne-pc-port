"""Independently cross-check all LSDA-bearing FDEs with Ghidra; no targets supplied."""
import hashlib,json,subprocess,sys
from pathlib import Path
from tools.formats import ElfImage
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
regions=json.loads((root/"local/cfg/exceptions-v2/regions.json").read_text())
modules=json.loads((root/"local/analysis/transitive-modules.json").read_text())["modules"]
results=[]
for module in modules:
 selected=[r for r in regions if r["module"]==module["sha256"]]
 if not selected:continue
 raw=Path(module["file"]).read_bytes();assert hashlib.sha256(raw).hexdigest()==module["sha256"]
 im=ElfImage(raw);folder=out/Path(module["file"]).name;folder.mkdir()
 segments=[]
 for n,s in enumerate(im.segments):
  if s.type not in (1,0x61000010) or not s.filesz:continue
  path=folder/f"segment-{n}.bin";path.write_bytes(im.file_bytes(s.offset,s.filesz))
  segments.append(dict(name=f"supplied_segment_{n}",rva=s.vaddr,path=str(path)))
 manifest=folder/"input.json";manifest.write_bytes((json.dumps(dict(module_sha256=module["sha256"],segments=segments,fdes=[r["fde"] for r in selected]),indent=2)+"\n").encode())
 dummy=folder/"dummy.bin";dummy.write_bytes(b"\0")
 projects=folder/"projects";projects.mkdir()
 command=[sys.executable,"tools/ghidra_headless.py",str(projects),"exceptions",
  "-import",str(dummy),"-loader","BinaryLoader","-loader-baseAddr","0x7000000000",
  "-processor","x86:LE:64:default","-cspec","gcc","-noanalysis","-max-cpu","2",
  "-scriptPath",str(root/"tools/ghidra_scripts"),"-postScript","BBCheckExceptions.java",
  str(manifest),str(folder/"ghidra.json"),"-log",str(folder/"application.log"),"-scriptlog",str(folder/"script.log")]
 with (folder/"stdout.log").open("wb") as stdout,(folder/"stderr.log").open("wb") as stderr:
  result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=240)
 if result.returncode:raise RuntimeError(f"Ghidra exited {result.returncode}: {folder}")
 if not (folder/"ghidra.json").exists():raise RuntimeError(f"Ghidra result missing: {folder}")
 actual=json.loads((folder/"ghidra.json").read_text())
 expected=[dict(fde=r["fde"],start=r["start"],size=r["size"],lsda=r["lsda"],
                call_sites=[{k:c[k] for k in ("start","length","landing_pad","action")} for c in r["call_sites"]]) for r in selected]
 differences=[dict(expected=e,actual=a) for e,a in zip(expected,actual) if e!=a]
 if len(actual)!=len(expected):differences.append(dict(expected_count=len(expected),actual_count=len(actual)))
 (folder/"comparison.json").write_bytes((json.dumps(dict(equal=not differences,differences=differences),indent=2)+"\n").encode())
 if differences:raise RuntimeError(f"Independent exception comparison failed: {folder}/comparison.json")
 row=dict(module_sha256=module["sha256"],name=Path(module["file"]).name,regions=len(actual),call_sites=sum(len(r["call_sites"]) for r in actual))
 results.append(row);print(json.dumps(row),flush=True)
report=dict(status="pass",ghidra_version="12.1.3",modules=results,limitations="Agreement covers FDE range, LSDA address, and all call-site intervals/landing pads/action indices. No CFI execution, type matching or runtime exception propagation was tested.")
(out/"summary.json").write_bytes((json.dumps(report,indent=2)+"\n").encode())
print(json.dumps(report),flush=True)
