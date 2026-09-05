"""Launch pinned Ghidra's headless Java entry with workspace-local settings/caches."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ghidra=root/"external/toolchains/ghidra-12.1.3/ghidra_12.1.3_PUBLIC"
jdk=root/"external/toolchains/temurin-21.0.12.1/jdk-21.0.12.1+1"
args=[]
for line in (ghidra/"support/launch.properties").read_text().splitlines():
 if line.startswith(("VMARGS=","VMARGS_WINDOWS=")):args.append(line.split("=",1)[1])
for kind in ("settings","cache","temp","home"):
 (root/"local/tool-profiles/ghidra"/kind).mkdir(parents=True,exist_ok=True)
args += [f"-Dapplication.{kind}dir={root/'local/tool-profiles/ghidra'/folder}" for kind,folder in (("settings","settings"),("cache","cache"),("temp","temp"))]
args += [f"-Duser.home={root/'local/tool-profiles/ghidra/home'}","-Djava.awt.headless=true",
 "-Xmx4G","-XX:ParallelGCThreads=2","-XX:CICompilerCount=2",
 "-cp",str(ghidra/"Ghidra/Framework/Utility/lib/Utility.jar"),"ghidra.Ghidra",
 "ghidra.app.util.headless.AnalyzeHeadless",*sys.argv[1:]]
command=[str(jdk/"bin/java.exe"),*args]
print(json.dumps(dict(argv=command,launcher_reference="pinned support/launch.bat and launch.properties")),file=sys.stderr,flush=True)
raise SystemExit(subprocess.run(command,cwd=root).returncode)
