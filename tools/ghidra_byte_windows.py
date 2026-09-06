"""Independent SLEIGH decode of explicitly bounded byte windows (not function claims)."""
import argparse,json,sqlite3,subprocess,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.formats import ElfImage

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('windows',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 c=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);requests=json.loads(a.windows.read_text(encoding='utf-8'));selected=[];results=[]
 assert len({(r['module'],r['start']) for r in requests})==len(requests)
 for h,path,name in c.execute('select hash,path,name from module order by name'):
  entries=[dict(start=r['start'],end=r['end']) for r in requests if r['module']==h]
  if not entries:continue
  assert sha(path)==h and all(0<r['end']-r['start']<=32768 for r in entries)
  im=ElfImage(Path(path).read_bytes());folder=a.out/name;folder.mkdir();segments=[]
  for n,s in enumerate(im.segments):
   if s.type not in (1,0x61000010) or not s.filesz or not s.flags&1:continue
   target=folder/f'segment-{n}.bin';target.write_bytes(im.file_bytes(s.offset,s.filesz));segments.append(dict(name=f'mapped_{n}',rva=s.vaddr,path=str(target.resolve())))
  write_json(folder/'input.json',dict(module_sha256=h,segments=segments,entries=entries));dummy=folder/'dummy.bin';dummy.write_bytes(b'\0');(folder/'projects').mkdir()
  command=[sys.executable,'tools/ghidra_headless.py',str((folder/'projects').resolve()),'windows','-import',str(dummy.resolve()),'-loader','BinaryLoader','-loader-baseAddr','0x7000000000','-processor','x86:LE:64:default','-cspec','gcc','-noanalysis','-max-cpu','2','-scriptPath',str(Path('tools/ghidra_scripts').resolve()),'-postScript','BBCheckRecovery.java',str((folder/'input.json').resolve()),str((folder/'ghidra.json').resolve()),'-log',str((folder/'application.log').resolve()),'-scriptlog',str((folder/'script.log').resolve())]
  with (folder/'stdout.log').open('wb') as stdout,(folder/'stderr.log').open('wb') as stderr:result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=600)
  assert result.returncode==0 and (folder/'ghidra.json').exists(),folder
  actual=json.loads((folder/'ghidra.json').read_text(encoding='utf-8'));assert [(r['start'],r['end']) for r in actual]==[(r['start'],r['end']) for r in entries]
  selected.extend((h,r['start']) for r in entries);results.append(dict(module=h,name=name,windows=len(actual),instructions=sum(len(r['instructions']) for r in actual),raw_sha256=sha(folder/'ghidra.json')))
 assert set(selected)=={(r['module'],r['start']) for r in requests}
 summary=dict(status='independent bounded window decode complete',source_db_sha256=sha(a.source/'analysis.sqlite'),requests_sha256=sha(a.windows),modules=results,windows=len(selected),instructions=sum(r['instructions'] for r in results),limitations='Analysis windows only. No expected instruction addresses, targets or no-return contracts supplied; no execution or proven function extents.')
 write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
