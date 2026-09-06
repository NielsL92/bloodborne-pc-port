"""Match exact recovered floating-state instructions to authored selectors."""
import collections,json,re,sqlite3,subprocess,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);lifter=Path(sys.argv[2]).resolve();sem=Path(sys.argv[3]).resolve();source=root/'local/cfg/startup-recovery-v22-cache-repeat'
identity=json.loads((sem/'identity.json').read_text(encoding='utf-8'));bindings={}
for path,digest in identity['extension_sha256'].items():
 p=Path(path);assert sha(p)==digest
 for selector,implementation in re.findall(r'DEF_ISEL\(([A-Za-z0-9_]+)\)\s*=\s*(BB[A-Za-z0-9_]+)',p.read_text(encoding='utf-8')):bindings[selector]=dict(implementation=implementation,source=p.relative_to(root).as_posix())
assert sha(sem/'amd64_avx.bc')==identity['semantics_sha256']
c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
sites=[dict(r) for r in c.execute("select * from recovery_instruction where mnemonic like 'f%' or mnemonic in ('wait','ldmxcsr','stmxcsr','vldmxcsr','vstmxcsr') order by module,rva")]
assert len(sites)==360
rows=[];roots=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for n,site in enumerate(sites):
 code=bytes.fromhex(site['bytes']);decoded=list(decoder.disasm(code,site['rva']));assert len(decoded)==1 and decoded[0].size==site['size'] and decoded[0].mnemonic==site['mnemonic'] and decoded[0].op_str==site['operands']
 pc=0x100c00000+n*32;site['catalog_pc']=pc;roots.append(pc);rows.extend([dict(address=pc,bytes=site['bytes']),dict(address=pc+len(code),bytes='c3')])
write_json(out/'input.json',dict(roots=roots,instructions=rows));argv=list(map(str,[lifter,out/'input.json',out/'function.bc',out/'function.ll',out/'audit.json',sem]))
with (out/'lift.stdout').open('wb') as stdout,(out/'lift.stderr').open('wb') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=180)
write_json(out/'steps.json',[dict(argv=argv,exit_code=r.returncode)]);assert r.returncode==0
report=json.loads((out/'audit.json').read_text(encoding='utf-8'));assert len(report['decoded_addresses'])==720 and not report['missing_instruction_starts'] and not report['unvisited_manifest_instructions'];selectors={r['address']:r for r in report['decoded_selectors']};problems=[]
for site in sites:
 selected=selectors[site['catalog_pc']];site.update(selector=selected['selector'],implementation=selected['implementation']);binding=bindings.get(selected['selector']);site['authored_binding']=binding
 if not selected['lifted'] or not binding or binding['implementation'] not in selected['implementation']:problems.append(site)
write_json(out/'sites.json',sites);write_json(out/'problems.json',problems)
entries=set()
for module in sorted({r['module'] for r in sites}):
 addresses=[r['rva'] for r in sites if r['module']==module];owners=collections.defaultdict(list)
 for row in c.execute('select rva,entry from recovery_owner where module=? and rva in ('+','.join('?' for _ in addresses)+') order by rva,entry',[module,*addresses]):owners[row['rva']].append(row['entry']);entries.add((module,row['entry']))
 for site in sites:
  if site['module']==module:site['owners']=owners[site['rva']]
write_json(out/'sites.json',sites);write_json(out/'entries.json',[dict(module=m,start=e) for m,e in sorted(entries)])
rejected=[dict(module=m,start=e) for m,e in sorted(entries) if e in [0x30430,0x53cd0]];assert len(rejected)==2;write_json(out/'remaining-rejections.json',rejected)
ir=(out/'function.ll').read_text(encoding='utf-8');assert '__remill_fpu_' not in ir and 'x86_fp80' not in ir
summary=dict(status='exact recovered floating-state selector inventory retained; no startup promotion',sites=len(sites),x87_sites=sum(r['mnemonic'].startswith('f') or r['mnemonic']=='wait' for r in sites),mxcsr_sites=sum('mxcsr' in r['mnemonic'] for r in sites),owners=len(entries),problem_count=len(problems),selectors=dict(collections.Counter(r['selector'] for r in sites)),database_sha256=sha(source/'analysis.sqlite'),manifest_sha256=sha(source/'compilation-manifest.jsonl'),lifter_sha256=sha(lifter),semantics_sha256=sha(sem/'amd64_avx.bc'),sites_sha256=sha(out/'sites.json'),execution='none; exact bytes placed at isolated catalog PCs with an authored RET. This checks binding selection, not original function execution, effects or runtime closure.')
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True);assert not problems
