"""Check fail-closed promotion contracts with minimized synthetic IR."""
import json,subprocess,sys
from pathlib import Path
root=Path.cwd();out=root/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
tool=root/"build/state-promotion/bb-state-promotion.exe"
prefix='target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"\n'
cases={
 "valid":("store i64 %pc, ptr %s\nret ptr %m",0),
 "escaped":("store ptr %s, ptr %m\nret ptr %m",2),
 "volatile":("store volatile i64 %pc, ptr %s\nret ptr %m",2),
 "variable_offset":("%p = getelementptr i8, ptr %s, i64 %pc\nstore i64 1, ptr %p\nret ptr %m",2),
 "outside_state":("%p = getelementptr i8, ptr %s, i64 3504\nstore i64 1, ptr %p\nret ptr %m",2),
 "unknown_boundary":("call void @unknown(ptr %s)\nret ptr %m",2),
 "atomic_state":("store atomic i64 %pc, ptr %s seq_cst, align 8\nret ptr %m",2)}
results=[]
for name,(body,expected) in cases.items():
 source=out/(name+".ll");dest=out/(name+"-out.ll")
 source.write_bytes((prefix+"declare void @unknown(ptr)\ndefine ptr @sub_test(ptr %s, i64 %pc, ptr %m) {\n"+body+"\n}\n").encode())
 r=subprocess.run([str(tool),str(source),str(dest)],capture_output=True,timeout=30)
 (out/(name+".stdout")).write_bytes(r.stdout);(out/(name+".stderr")).write_bytes(r.stderr)
 assert r.returncode==expected,(name,r.returncode,r.stderr.decode())
 assert dest.exists()==(expected==0)
 if expected:assert b"REJECT:" in r.stderr
 results.append(dict(case=name,exit=r.returncode,diagnostic=r.stderr.decode().strip()))
(out/"summary.json").write_bytes((json.dumps(results,indent=2)+"\n").encode())
print(json.dumps(results))
