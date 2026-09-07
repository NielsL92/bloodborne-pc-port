"""Extend a previously recorded native startup command into fresh experiment directories."""
import argparse,json,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import write_json
p=argparse.ArgumentParser();p.add_argument('from_run');p.add_argument('out',type=Path);p.add_argument('--id',required=True);p.add_argument('--supplement',type=Path);a=p.parse_args();record=json.loads((Path('local/runs')/a.from_run/'manifest.json').read_text(encoding='utf-8'));assert record['status']=='pass';argv=record['argv'];assert argv[1:3]==['-m','tools.native_startup_experiment'] and argv[3]=='local/runtime/startup-entry-contract-v1';assert not a.out.exists();argv=argv[:];argv[0]=sys.executable;argv[4]=str(a.out)
if a.supplement:argv.extend(['--supplement',str(a.supplement)])
raise SystemExit(subprocess.run([sys.executable,'tools/run_record.py','--id',a.id,'--',*argv]).returncode)
