"""Reject malformed or inapplicable source-level nonreturn contracts."""
import argparse,copy,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('lifter',type=Path);p.add_argument('semantics',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
pc=0x1000a0000
base=dict(roots=[pc,pc+32],instructions=[dict(address=pc,bytes='e81b000000'),dict(address=pc+5,bytes='c3'),dict(address=pc+32,bytes='c3')],return_contracts=[dict(address=pc,expected_next_pc=pc+5,kind='no-normal-return',provenance='authored input assertion')])
cases=[('valid',base,True,'')]
for name,edit,diagnostic in [
 ('container_type',lambda d:d.update(return_contracts={}), 'return_contracts must be an array'),
 ('row_type',lambda d:d.update(return_contracts=[3]), 'invalid return contract'),
 ('missing_source',lambda d:d['return_contracts'][0].pop('address'), 'address field'),
 ('unknown_source',lambda d:d['return_contracts'][0].update(address=pc+1,expected_next_pc=pc+6), 'invalid exact nonreturn contract'),
 ('wrong_next',lambda d:d['return_contracts'][0].update(expected_next_pc=pc+6), 'invalid exact nonreturn contract'),
 ('unknown_kind',lambda d:d['return_contracts'][0].update(kind='maybe-return'), 'invalid exact nonreturn contract'),
 ('empty_provenance',lambda d:d['return_contracts'][0].update(provenance=''), 'invalid exact nonreturn contract'),
 ('missing_provenance',lambda d:d['return_contracts'][0].pop('provenance'), 'invalid exact nonreturn contract'),
 ('duplicate',lambda d:d['return_contracts'].append(d['return_contracts'][0].copy()), 'invalid exact nonreturn contract'),
 ('not_a_call',lambda d:d['return_contracts'][0].update(address=pc+32,expected_next_pc=pc+33), 'actual ordinary call'),
 ('call_next_contract',lambda d:d['instructions'][0].update(bytes='e800000000'), 'actual ordinary call'),
]:
 d=copy.deepcopy(base);edit(d);cases.append((name,d,False,diagnostic))
d=dict(roots=[pc],instructions=[dict(address=pc,bytes='e800000000'),dict(address=pc+5,bytes='58'),dict(address=pc+6,bytes='c3')]);cases.append(('call_next_idiom',d,True,''))
# A valid CALL assertion in bytes that no root visits must also be rejected.
d=copy.deepcopy(base);d['instructions'] += [dict(address=pc+64,bytes='e8dbffffff')];d['return_contracts']=[dict(address=pc+64,expected_next_pc=pc+69,kind='no-normal-return',provenance='unvisited authored call')];cases.append(('unvisited_contract',d,False,'declared nonreturn contract was not guarded'))
results=[]
for name,data,accept,diagnostic in cases:
 folder=a.out/name;folder.mkdir();write_json(folder/'input.json',data);argv=[str(a.lifter.resolve()),str((folder/'input.json').resolve()),str((folder/'function.bc').resolve()),str((folder/'function.ll').resolve()),str((folder/'audit.json').resolve()),str(a.semantics.resolve())]
 proc=subprocess.run(argv,capture_output=True,timeout=120);(folder/'lift.stdout').write_bytes(proc.stdout);(folder/'lift.stderr').write_bytes(proc.stderr);stderr=proc.stderr.decode('utf-8',errors='replace');assert (proc.returncode==0)==accept,(name,stderr);assert diagnostic in stderr,(name,stderr)
 if accept:
  audit=json.loads((folder/'audit.json').read_text(encoding='utf-8'));assert not audit['unvisited_manifest_instructions'];assert len(audit['call_return_checks'])==(1 if name=='valid' else 0)
 else:assert not (folder/'function.bc').exists() and not (folder/'function.ll').exists()
 results.append(dict(case=name,accept=accept,exit_code=proc.returncode,diagnostic=diagnostic,input_sha256=sha(folder/'input.json'),stderr_sha256=sha(folder/'lift.stderr')))
summary=dict(status='pass',cases=len(results),accepted=sum(r['accept'] for r in results),rejected=sum(not r['accept'] for r in results),results=results,lifter_sha256=sha(a.lifter),semantics_sha256=sha(a.semantics/'amd64_avx.bc'),game_execution=False);write_json(a.out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='results'}),flush=True)
