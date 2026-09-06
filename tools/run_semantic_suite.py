"""Run the authored semantic contracts against one pinned combined module."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('driver',type=Path);p.add_argument('semantics',type=Path);p.add_argument('--families',nargs='+',default=['bmi','shuffle','blend','rsqrt','packed','select','transfer','minmax','round','sqrt']);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);results={}
for family in a.families:
 assert family in ('bmi','shuffle','blend','rsqrt','packed','select','transfer','minmax','round','sqrt') and family not in results
 tool='tools.bmi_semantics_checks' if family=='bmi' else 'tools.shuffle_semantics_checks' if family=='shuffle' else 'tools.vector_semantics_checks'
 argv=[sys.executable,'-m',tool,*([family] if tool.endswith('vector_semantics_checks') else []),str(a.out/family),str(a.driver),str(a.semantics)]
 with (a.out/(family+'.stdout')).open('wb') as stdout,(a.out/(family+'.stderr')).open('wb') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=240)
 assert r.returncode==0,family
 summary=json.loads((a.out/family/'summary.json').read_text());assert summary['semantics_sha256']==sha(a.semantics/'amd64_avx.bc')
 results[family]=dict(argv=argv,summary=summary);write_json(a.out/'summary.json',dict(status='running',results=results));print(family+': '+json.dumps(summary['result']),flush=True)
write_json(a.out/'summary.json',dict(status='combined authored semantic suite pass',results=results,semantics_sha256=sha(a.semantics/'amd64_avx.bc'),driver_sha256=sha(a.driver),game_code_execution=False))
