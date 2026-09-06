"""Challenge the LLVM memory-source audit with authored AOT and malformed sources."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('inspector',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def inspect(source,name):
 out=a.out/(name+'.json');r=subprocess.run([str(a.inspector.resolve()),str(source.resolve()),str(out.resolve())],capture_output=True,timeout=120);(a.out/(name+'.stdout')).write_bytes(r.stdout);(a.out/(name+'.stderr')).write_bytes(r.stderr);assert r.returncode==0;return json.loads(out.read_text())
for name in ['guards-v4-repeat','fp-v4-memory-sources','control-v7-memory-sources/source','control-v7-memory-sources/target']:
 folder=Path('local/runtime')/name;report=inspect(folder/'function.bc',name.replace('/','-'));memory=report['memory_source_audit'];audit=json.loads((folder/'audit.json').read_text());data=json.loads((folder/'input.json').read_text());assert not memory['invalid_sites'] and not memory['legacy_memory_calls'];assert memory['counts']==audit['native_memory_bridges'];assert {int(v,16) for v in memory['source_pcs']}<={i['address'] for i in data['instructions']}
head='declare i64 @__bb_sourced_read_memory_64(ptr,i64,ptr,i64) nounwind'+chr(10)+'declare void @escape(ptr)'+chr(10)
cases=[]
for n in range(7):
 lines=[head,'define ptr @sub_1000(ptr %s,i64 %pc,ptr %m) {','entry:',' %BB_SOURCE_PC = alloca i64',' store i64 17,ptr %BB_SOURCE_PC']
 if n==1:lines+=[' call void @escape(ptr %BB_SOURCE_PC)']
 if n==2:lines+=[' store i64 %pc,ptr %BB_SOURCE_PC']
 if n==3:lines+=[' store i64 0,ptr %BB_SOURCE_PC']
 if n==4:lines+=[' ret ptr %m','dead:']
 lines+=[' %v=load i64,ptr %BB_SOURCE_PC']
 source='%pc' if n==5 else '%v';state='%m' if n==6 else '%s'
 lines+=[f' %r=call i64 @__bb_sourced_read_memory_64(ptr {state},i64 {source},ptr %m,i64 32)',' ret ptr %m','}'];path=a.out/f'case-{n}.ll';path.write_text(chr(10).join(lines)+chr(10),encoding='utf-8');report=inspect(path,f'case-{n}');assert len(report['memory_source_audit']['invalid_sites'])==(n!=0);cases.append(dict(case=n,rejected=n!=0))
write_json(a.out/'summary.json',dict(status='independent LLVM memory-source checks pass',authored_objects=4,synthetic_cases=cases,inspector_sha256=sha(a.inspector),game_execution=False));print('LLVM memory-source checks pass',flush=True)
