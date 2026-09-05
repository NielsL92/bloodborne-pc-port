"""Contract-only memory lowering; not suitable for MMIO, untrusted mappings or atomics."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("output");a=p.parse_args()
s=Path(a.source).read_text();definitions=[]
for line in s.splitlines():
 m=re.match(r"declare (.*?) @(__remill_[^(]+)\((.*)\).*",line)
 if not m:continue
 ret,name,args=m.groups();body=None
 if name.startswith("__remill_flag_computation_") or name.startswith("__remill_compare_"):
  body=f"define internal i1 @{name}(i1 %v"+(", ..." if "..." in args else "")+") alwaysinline {\n ret i1 %v\n}\n"
 elif name=="__remill_undefined_8":
  body=f"define internal i8 @{name}() alwaysinline {{\n ret i8 0\n}}\n"
 else:
  mm=re.fullmatch(r"__remill_(read|write)_memory_(8|16|32|64|f32|f64)",name)
  if mm:
   op,width=mm.groups();ty={"f32":"float","f64":"double"}.get(width,"i"+width)
   if op=="read":body=f"define internal {ty} @{name}(ptr %m, i64 %a) alwaysinline {{\n %p = inttoptr i64 %a to ptr\n %v = load {ty}, ptr %p, align 1\n ret {ty} %v\n}}\n"
   else:body=f"define internal ptr @{name}(ptr %m, i64 %a, {ty} %v) alwaysinline {{\n %p = inttoptr i64 %a to ptr\n store {ty} %v, ptr %p, align 1\n ret ptr %m\n}}\n"
 if body:s=s.replace(line,body)
Path(a.output).write_text(s)
