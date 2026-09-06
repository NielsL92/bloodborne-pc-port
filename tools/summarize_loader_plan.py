"""Verify reproducible module data/relocation plans and retained unresolved work."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
x=ROOT/'local/runtime/loader-plan-v4-weak';y=ROOT/'local/runtime/loader-plan-v5-repeat';artifacts={}
for path in sorted(x.iterdir()):assert path.read_bytes()==(y/path.name).read_bytes(),path.name;artifacts[path.name]=sha(path)
summary=json.loads((y/'summary.json').read_text());assert summary['unresolved_relocations']==752 and summary['code_relocations']==0 and summary['constructor_targets_checked']==18444 and summary['version_disputes']==0 and not summary['game_execution'];assert summary['classification']['checked absent weak callback']==12
weak=ROOT/'local/runtime/loader-weak-v3-source-identity';assert summary['weak_bindings_sha256']==sha(weak/'weak-bindings.json');proof=json.loads((weak/'summary.json').read_text());assert proof['ghidra_checked'] and proof['bindings']==12
records=[]
for name in ['20260906-p4-loader-weak-v3-source-identity','20260906-p4-ghidra-loader-weak-v1','20260906-p4-loader-plan-v4-weak','20260906-p4-loader-plan-v5-repeat']:
 p=ROOT/'local/runs'/name/'manifest.json';r=json.loads(p.read_text());assert r['status']=='pass';records.append(dict(run=name,manifest_sha256=sha(p)))
result=dict(status='P4 loader plan reproducible; loading/execution remain open',plan=summary,weak=proof,identical_artifacts=artifacts,recorders=records,p4_gate_passed=False,next='Resolve external function identity, twenty strong data imports and seventeen TLS references; then validate private native loading.')
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],identical_artifacts=len(artifacts),unresolved_relocations=752)),flush=True)
