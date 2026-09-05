"""Focused P3 evidence audit; does not execute original code or rehash PKGs."""
import ast,hashlib,json,sqlite3,sys,zipfile
from pathlib import Path
root=Path.cwd()
def read(path):return json.loads((root/path).read_text())
paths={
 "metadata":"local/cfg/seed-v1/summary.json","metadata_repeat":"local/cfg/seed-v2/summary.json",
 "switch_check":"local/cfg/ghidra-bitreader-v1/summary.json",
 "exception_metadata":"local/cfg/exceptions-v2/summary.json",
 "exception_check":"local/cfg/ghidra-exceptions-v2/summary.json",
 "startup_inventory":"local/cfg/startup-v1/summary.json",
 "startup_check":"local/cfg/ghidra-startup-v1/summary.json",
 "startup_frontier":"local/cfg/startup-db-v1/summary.json"}
evidence={name:dict(path=path,sha256=hashlib.sha256((root/path).read_bytes()).hexdigest(),result=read(path)) for name,path in paths.items()}
assert evidence["metadata"]["result"]["db_sha256"]==evidence["metadata_repeat"]["result"]["db_sha256"]
for key in ("switch_check","exception_check","startup_check"):assert evidence[key]["result"]["status"]=="pass"
assert evidence["exception_metadata"]["result"]["counts"]["exception_issue"]==0
surveys=[]
for n in range(1,6):
 p=f"local/cfg/survey-v{n}/summary.json";r=read(p)
 surveys.append(dict(path=p,sha256=hashlib.sha256((root/p).read_bytes()).hexdigest(),counts=r["counts"],issue_kinds=r["issue_kinds"],edge_kinds=r["edge_kinds"],independent_switch_instruction_set_equal=r["independent_switch_instruction_set_equal"]))
assert surveys[-1]["issue_kinds"]=={"fallthrough_at_range_end":42}
db_path=root/"local/cfg/startup-db-v1/analysis.sqlite"
assert hashlib.sha256(db_path.read_bytes()).hexdigest()==evidence["startup_frontier"]["result"]["db_sha256"]
db=sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro",uri=True)
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
assert db.execute("SELECT count(*) FROM initializer_slot").fetchone()[0]==18444
assert db.execute("SELECT count(*) FROM exception_region").fetchone()[0]==225
assert db.execute("SELECT count(*) FROM exception_call_site").fetchone()[0]==1223
def historical_evidence_matches(path, digest):
 file=Path(path)
 if file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest()==digest:return True
 # Source files evolve. Verify old evidence against immutable recorded source snapshots.
 try:relative=file.resolve().relative_to(root.resolve()).as_posix()
 except ValueError:return False
 for manifest_path in sorted((root/'local/runs').glob('*/manifest.json')):
  manifest=json.loads(manifest_path.read_text())
  hashes={k.replace('\\','/').replace(chr(92),'/'):v for k,v in manifest.get('source_sha256',{}).items()}
  if hashes.get(relative)!=digest:continue
  archive=manifest_path.parent/'sources.zip'
  if not archive.exists():continue
  with zipfile.ZipFile(archive) as snapshot:
   names={n.replace(chr(92),'/'):n for n in snapshot.namelist()}
   if relative in names and hashlib.sha256(snapshot.read(names[relative])).hexdigest()==digest:return True
 return False
for kind,path,sha in db.execute("SELECT * FROM analysis_evidence"):
 assert historical_evidence_matches(path,sha),(kind,path)
db.close()
runs={}
for name in ("20260905-p3-recursive-survey-v1","20260905-p3-recursive-survey-v2","20260905-p3-recursive-survey-v3","20260905-p3-metadata-repeat","20260905-p3-exception-metadata-v2","20260905-p3-ghidra-exceptions-v2","20260905-p3-exception-reader-checks","20260905-p3-recursive-survey-v4","20260905-p3-recursive-survey-v5","20260905-p3-startup-roots-v1","20260905-p3-ghidra-startup-v1","20260905-p3-startup-frontier-v1"):
 manifest=read(f"local/runs/{name}/manifest.json");assert manifest["status"]=="pass"
 runs[name]=dict(status=manifest["status"],source_commit=manifest["project_commit"],elapsed_seconds=manifest["elapsed_seconds"])
for p in list((root/"tools").glob("*cfg*.py"))+list((root/"tools").glob("*exception*.py"))+list((root/"tools").glob("*startup*.py"))+[root/"tests/test_exception_metadata.py"]:
 ast.parse(p.read_text(),filename=str(p))
result=dict(status="focused P3 evidence consistency pass; startup closure gate remains open",evidence=evidence,surveys=surveys,runs=runs,
 retained_failures=[
 dict(run="20260905-p3-exception-metadata-v1",reason="Duplicate lsda keyword while merging metadata dictionaries; corrected before v2."),
 dict(run="20260905-p3-ghidra-exceptions-v1",reason="37 omitted-null JSON differences; all numerical values agreed. serializeNulls fixed, both modules passed fresh v2.")],
 native_game_boot=False,native_port_playable=False,gate="P3 not passed: startup query stops at 18437 undecoded entries; indirect/mutable targets and native control/service contracts remain open.")
latest=root/'reports/startup-recovery-evidence.json'
if latest.exists():
 recovery=json.loads(latest.read_text())
 assert recovery['status']=='startup recovery evidence consistency pass; P3 gate open'
 result['startup_recovery']=dict(path=str(latest.relative_to(root)),sha256=hashlib.sha256(latest.read_bytes()).hexdigest(),result=recovery)
 result['gate']=recovery['gate']
(root/"reports/control-flow-evidence.json").write_bytes((json.dumps(result,indent=2)+"\n").encode())
print(json.dumps({k:v for k,v in result.items() if k not in ("evidence","surveys","runs","startup_recovery")}),flush=True)
