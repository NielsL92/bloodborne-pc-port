"""Check conservative LLVM source provenance, including escaped/dynamic slots."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('inspector',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
def run(source,name):
 output=a.out/(name+'.json');r=subprocess.run([str(a.inspector.resolve()),str(source.resolve()),str(output.resolve())],capture_output=True,timeout=120);(a.out/(name+'.stdout')).write_bytes(r.stdout);(a.out/(name+'.stderr')).write_bytes(r.stderr);assert r.returncode==0;return json.loads(output.read_text(encoding='utf-8'))
fixture=Path('local/compiler-spike/source-exit-checks-v3-repeat/function.bc');report=run(fixture,'authored');sites=[s for s in report['sites'] if s['callee']=='__bb_native_block_transfer'];assert len(sites)==6
for s in sites:
 pc=int(s['function'][4:],16);n=(pc-0x1000b0000)//256;expected={pc+2,pc+4} if n in [2,5] else {pc+4} if n==3 else {pc};arg=s['arguments'][3];assert arg['integer_origins_complete'] and {int(v,16) for v in arg['possible_integer_values_hex']}==expected and s['cfg_reachable_from_entry']
text='declare ptr @__bb_native_block_transfer(ptr,i64,ptr,i64,i64)\ndeclare void @escape(ptr)\n'
for n in range(4):
 text+=f'define ptr @sub_{0x1000+n:x}(ptr %s,i64 %pc,ptr %m) {{\nentry:\n  %BB_SOURCE_PC = alloca i64\n  store i64 17,ptr %BB_SOURCE_PC\n'
 if n==1:text+='  call void @escape(ptr %BB_SOURCE_PC)\n'
 if n==2:text+='  store i64 %pc,ptr %BB_SOURCE_PC\n'
 if n==3:text+='  ret ptr %m\ndead:\n'
 text+='  %v=load i64,ptr %BB_SOURCE_PC\n  %r=call ptr @__bb_native_block_transfer(ptr %s,i64 %pc,ptr %m,i64 %v,i64 32)\n  ret ptr %r\n}\n'
source=a.out/'synthetic.ll';source.write_text(text,encoding='utf-8');negative=run(source,'synthetic');tests=[s for s in negative['sites'] if s['callee']=='__bb_native_block_transfer'];assert len(tests)==4
for s in tests:
 n=int(s['function'][4:],16)-0x1000;assert s['cfg_reachable_from_entry']==(n!=3);assert s['arguments'][3]['integer_origins_complete']==(n==0)
summary=dict(status='read-only source origin and CFG reachability checks pass',authored_transfer_sites=6,synthetic_cases=4,inspector_sha256=sha(a.inspector),artifact_sha256={name:sha(a.out/name) for name in ['authored.json','synthetic.ll','synthetic.json']},game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
