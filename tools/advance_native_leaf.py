"""Advance a bounded number of observed native leaf dependencies with recorded checks."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('from_run');p.add_argument('out',type=Path);p.add_argument('--label',required=True);p.add_argument('--first-index',type=int,required=True);p.add_argument('--count',type=int,default=3);a=p.parse_args();assert 1<=a.count<=3 and a.label.replace('-','').isalnum();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));initial=read(Path('local/runs')/a.from_run/'manifest.json');assert initial['status']=='pass';argv=initial['argv'];assert argv[1:3]==['-m','tools.native_startup_experiment'];assert argv[3]=='local/runtime/startup-entry-contract-v1';assert '--trace-calls' in argv and '--tls' in argv;source='local/cfg/startup-recovery-v31-conditional-repeat';registry='local/runtime/registry-v7-memory-repeat';steps=[]
def run(tag,module,args):
 run_id='20260907-p4-'+a.label+'-'+tag;command=[sys.executable,'tools/run_record.py','--id',run_id,'--',sys.executable,'-m',module,*map(str,args)]
 with (a.out/(tag+'.stdout')).open('wb') as stdout,(a.out/(tag+'.stderr')).open('wb') as stderr:r=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=240)
 record=read(Path('local/runs')/run_id/'manifest.json');steps.append(dict(run=run_id,status=record['status'],manifest_sha256=sha(Path('local/runs')/run_id/'manifest.json')));write_json(a.out/'steps.json',steps);assert r.returncode==0 and record['status']=='pass',(tag,r.returncode);print(json.dumps(dict(completed=tag,run=run_id)),flush=True)
def stable(x):
 if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k!='thread'}
 if isinstance(x,list):return [stable(v) for v in x]
 return x
advances=[]
for i in range(a.count):
 previous=Path(argv[4]);before=read(previous/'summary.json');assert before['fault']['boundary']=='unknown-compiled-target' and before['fault']['reason']==27;pc=int(before['fault']['pc'],16);tag=f'{i+1}';prefix=a.label+'-'+tag
 recovery=Path('local/cfg')/(prefix+'-recovery');ghidra=Path('local/cfg')/(prefix+'-ghidra');first=Path('local/compiler-spike')/(prefix+'-compile');repeat=Path('local/compiler-spike')/(prefix+'-compile-repeat');manifest=Path('local/compiler-spike')/(prefix+'-manifest')
 run(tag+'-recover','tools.recover_linear_target',[previous,source,registry,recovery]);run(tag+'-ghidra','tools.ghidra_byte_windows',[source,recovery/'windows.json',ghidra]);run(tag+'-compile','tools.compile_native_leaf',[recovery,ghidra,first]);run(tag+'-compile-repeat','tools.compile_native_leaf',[recovery,ghidra,repeat]);run(tag+'-manifest','tools.supplemental_native_manifest',[first,repeat,registry,manifest])
 current=Path('local/runtime')/f'startup-v{a.first_index+i*2}-{prefix}';current_repeat=Path('local/runtime')/f'startup-v{a.first_index+i*2+1}-{prefix}-repeat';argv=argv[:];argv[4]=str(current);argv.extend(['--supplement',str(manifest)]);run(tag+'-startup','tools.native_startup_experiment',argv[3:]);argv[4]=str(current_repeat);run(tag+'-startup-repeat','tools.native_startup_experiment',argv[3:]);one,two=read(current/'summary.json'),read(current_repeat/'summary.json');assert stable(one)==stable(two)
 artifacts={}
 for path in current.iterdir():
  if path.suffix in ['.obj','.exe','.bin'] or path.name in ['probe-manifest.json','startup-config.h','expected-image.json','linked-roots.json','compilation-objects.json','compilation-targets.json','native-calls.jsonl','prepare.stdout','entry.stdout']:
   assert sha(path)==sha(current_repeat/path.name);artifacts[path.name]=sha(path)
 calls=[json.loads(s) for s in (current_repeat/'native-calls.jsonl').read_text(encoding='utf-8').splitlines()];returned=[r for r in calls if r['event']=='dispatch-return' and r['target']==pc];assert returned,hex(pc)
 advances.append(dict(pc=pc,previous_probe=str(previous),recovery=str(recovery),ghidra=str(ghidra),compiled=str(repeat),supplement=str(manifest),current=str(current_repeat),summary_sha256=sha(current_repeat/'summary.json'),returns=returned,artifacts=artifacts,next_fault=two['fault']));write_json(a.out/'advances.json',advances)
result=dict(status='bounded observed native leaf sequence completed with exact startup repeats',advances=advances,steps=steps,current_probe=argv[4],continuation_argv=argv,game_aot_execution=True,original_byte_cpu_execution=False,native_game_boot=False,p4_gate_passed=False,limitations=['Only the target requested by each actual native stop is recovered. Each next input must pass the strict supported-body grammar and independent checks.','No adjacent candidates, complete function/discovery closure or whole-game execution coverage are inferred.','Existing service, TLS, FP, data and control limitations remain; no original-byte execution fallback.']);write_json(a.out/'summary.json',result);print(json.dumps(dict(status=result['status'],current_probe=argv[4],next_fault=advances[-1]['next_fault'])),flush=True)
