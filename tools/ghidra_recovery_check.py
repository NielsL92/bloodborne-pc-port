"""Independently inspect startup constructors and disputed decode windows with Ghidra."""
import argparse,collections,json,sqlite3,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('--selection',type=Path);p.add_argument('--exception-roots',action='store_true');a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
db=sqlite3.connect(f'{(a.source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
main=db.execute("SELECT hash FROM module WHERE name='eboot.bin'").fetchone()[0]
roots=json.loads((a.source/'constructor-order.json').read_text())
selected={(main,r['target']):'ordered_constructor_sample' for r in roots[::max(1,len(roots)//96)]}
# All constructor disputes, then bounded deterministic examples of every other issue kind.
for h,start in db.execute('SELECT r.module,r.start FROM recovery_entry r JOIN initializer_slot s ON s.module=r.module AND s.target=r.start WHERE r.issues>0'):
 selected[h,start]='constructor_dispute'
for kind, in db.execute('SELECT DISTINCT kind FROM recovery_issue ORDER BY kind'):
 for h,start in db.execute('SELECT DISTINCT module,entry FROM recovery_issue WHERE kind=? ORDER BY module,entry LIMIT 12',(kind,)):
  selected[h,start]='decode_dispute_'+kind
# Explicitly investigate a string-as-code false positive from the retained first run.
if (a.source.parent/'startup-recovery-v1/analysis.sqlite').exists():
 selected['3b8eb4d5a5c5a7b381d8d0610077e6cd404c29695a686274802f6b2737f6bf22',255735]='retained_v1_string_pointer_dispute'
if a.selection:
 selected={(r['module'],r['start']):r['reason'] for r in json.loads(a.selection.read_text())}
results=[];selection=[]
for h,path,name in db.execute('SELECT hash,path,name FROM module ORDER BY name'):
 entries=[];im=None
 for (other,start),reason in sorted(selected.items()):
  if h!=other:continue
  row=db.execute('SELECT fence,issues FROM recovery_entry WHERE module=? AND start=?',(h,start)).fetchone()
  if not row:
   if reason!='retained_v1_string_pointer_dispute':continue
   row=(start+128,1)
  end=row[0]
  if end<=start:continue
  # Keep the test bounded; include a small following byte window for disputed endings.
  if end-start>32768:continue
  spec=dict(start=start,end=end+(32 if row[1] else 0),fence=end,reason=reason)
  if a.exception_roots:
   spec['additional_roots']=[r[0] for r in db.execute('SELECT DISTINCT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL ORDER BY landing_pad',(h,start))]
  entries.append(spec)
 if not entries:continue
 assert sha(path)==h
 im=ElfImage(Path(path).read_bytes());folder=a.out/name;folder.mkdir();segments=[]
 for n,s in enumerate(im.segments):
  if s.type not in (1,0x61000010) or not s.filesz or not s.flags&1:continue
  target=folder/f'segment-{n}.bin';target.write_bytes(im.file_bytes(s.offset,s.filesz))
  segments.append(dict(name=f'mapped_{n}',rva=s.vaddr,path=str(target.resolve())))
 write_json(folder/'input.json',dict(module_sha256=h,segments=segments,entries=entries))
 dummy=folder/'dummy.bin';dummy.write_bytes(b'\0');(folder/'projects').mkdir()
 command=[sys.executable,'tools/ghidra_headless.py',str((folder/'projects').resolve()),'recovery','-import',str(dummy.resolve()),
 '-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2',
 '-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckRecovery.java',str((folder/'input.json').resolve()),str((folder/'ghidra.json').resolve()),
 '-log',str((folder/'application.log').resolve()),'-scriptlog',str((folder/'script.log').resolve())]
 with (folder/'stdout.log').open('wb') as stdout,(folder/'stderr.log').open('wb') as stderr:
  result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=600)
 if result.returncode or not (folder/'ghidra.json').exists():raise RuntimeError(f'Ghidra failed; retained logs: {folder}')
 actual=json.loads((folder/'ghidra.json').read_text())
 for spec,got in zip(entries,actual,strict=True):
  assert spec['start']==got['start']
  expected={rva:(size,b) for rva,size,b in db.execute('SELECT i.rva,i.size,i.bytes FROM recovery_owner o CROSS JOIN recovery_instruction i ON i.module=o.module AND i.rva=o.rva WHERE o.module=? AND o.entry=?',(h,spec['start']))}
  recovered={r['rva']:(r['length'],r['bytes']) for r in got['instructions'] if r['rva']<spec['fence']}
  common=set(expected)&set(recovered)
  comparison=dict(module=h,**spec,equal=expected==recovered,expected_instructions=len(expected),ghidra_instructions=len(recovered),
   common_instructions=len(common),boundary_disagreements=[v for v in sorted(common) if expected[v]!=recovered[v]],
   only_recovery=sorted(set(expected)-set(recovered)),only_ghidra=sorted(set(recovered)-set(expected)))
  results.append(comparison)
 selection.extend(dict(module=h,**s) for s in entries)
 print(json.dumps(dict(module=name,checked=len(entries))),flush=True)
write_json(a.out/'selection.json',selection);write_json(a.out/'comparison.json',results)
summary=dict(status='independent inspection complete; disagreements retained',entries=len(results),equal=sum(r['equal'] for r in results),
 common_instructions=sum(r['common_instructions'] for r in results),boundary_disagreements=sum(len(r['boundary_disagreements']) for r in results),
 differing_entries=sum(not r['equal'] for r in results),comparison_sha256=sha(a.out/'comparison.json'),source_db_sha256=sha(a.source/'analysis.sqlite'),
 exception_roots_supplied=a.exception_roots,
 limitations='Independent SLEIGH decode from entry and bounded supplied bytes. Optional additional roots come from LSDA metadata. No expected instructions, jump-table targets, or no-return contracts supplied. Windows are analysis bounds, not independently proven function extents. No game execution or whole-startup completeness.')
write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
