"""Check canonical function identities, loader values and complete-link repeats."""
import argparse,json
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
artifacts={}
for first,second in [('services-v1','services-v2-repeat'),('registry-v4-services','registry-v5-service-identities'),('loader-plan-v6-services','loader-plan-v7-repeat'),('link-v6-services','link-v7-repeat')]:
 x=ROOT/'local/runtime'/first;y=ROOT/'local/runtime'/second
 for path in sorted(x.iterdir()):
  if not path.is_file() or (first.startswith('link') and not(path.suffix in ['.obj','.exe'] or path.name in ['linked-addresses.json','native-import-stops.json','validate.stdout'])):continue
  assert path.read_bytes()==(y/path.name).read_bytes(),(first,path.name);artifacts[first+'/'+path.name]=sha(path)
services=read(ROOT/'local/runtime/services-v2-repeat/native-services.json');registry=read(ROOT/'local/runtime/registry-v5-service-identities/imports.json');plan=ROOT/'local/runtime/loader-plan-v7-repeat';relocs={(r['module'],r['offset']):r for r in map(json.loads,(plan/'relocations.jsonl').read_text().splitlines())};native={r['pc']:r for r in registry if r.get('canonical')};checks=0
for service in services:
 assert all(native[service['pc']][k]==service[k] for k in ['nid','library','library_version','module','module_version'])
 for use in service['uses']:
  for rel in use['relocations']:
   actual=relocs[use['module'],rel['offset']];assert actual['kind']=='canonical native service identity';assert actual['value']==(service['pc']+(rel['addend'] if rel['type']==1 else 0))&0xffffffffffffffff;checks+=1
assert checks==831 and len(native)==len(services)==593
regions=read(plan/'regions.json');assert not any(r['base']<0xa00000000 and 0x900000000<r['base']+r['mapped_size'] for r in regions)
link=read(ROOT/'local/runtime/link-v7-repeat/summary.json');assert link['linked_game_roots']==21282 and link['linked_import_gateways']==775 and link['tested_unimplemented_import_stops']==708 and not link['game_execution'];loader=read(plan/'summary.json');assert loader['unresolved_relocations']==37 and loader['code_relocations']==0
records=[]
for name in ['20260906-p4-native-services-v1','20260906-p4-native-services-v2-repeat','20260906-p4-native-registry-v4-services','20260906-p4-native-registry-v5-service-identities','20260906-p4-loader-plan-v6-services','20260906-p4-loader-plan-v7-repeat','20260906-p4-native-link-v6-services','20260906-p4-native-link-v7-repeat']:
 file=ROOT/'local/runs'/name/'manifest.json';assert read(file)['status']=='pass';records.append(dict(run=name,manifest_sha256=sha(file)))
result=dict(status='canonical native function identity and full-link checks pass',services=read(ROOT/'local/runtime/services-v2-repeat/summary.json'),link=link,loader=loader,relocation_identity_checks=checks,identical_artifacts=artifacts,recorders=records,p4_gate_passed=False,limits='No game execution or native module loading. Canonical functions stop explicitly; strong-data and TLS references remain unresolved. Native logical module slot 9 is reserved and must not be reused by future module loading.')
write_json(a.out/'checked.json',result);print(json.dumps(dict(status=result['status'],identical_artifacts=len(artifacts),relocation_identity_checks=checks,remaining_unresolved_relocations=37)),flush=True)
