"""Cross-check duplicated COFF constants with raw records and LLVM readobj."""
import argparse,json,re,struct,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM

def raw_coff(data):
 machine,nsects,timestamp,symoff,nsyms,opt,flags=struct.unpack_from('<HHIIIHH',data);assert machine==0x8664 and opt==0 and nsects>0
 end=symoff+nsyms*18;strlen=struct.unpack_from('<I',data,end)[0];assert strlen>=4 and end+strlen<=len(data)
 def name(raw):
  if raw[:4]==bytes(4):
   off=struct.unpack_from('<I',raw,4)[0];assert 4<=off<strlen;stop=data.index(b'\0',end+off,end+strlen);return data[end+off:stop].decode('utf-8')
  return raw.rstrip(b'\0').decode('utf-8')
 sections={}
 for n in range(1,nsects+1):
  off=20+(n-1)*40;raw=data[off:off+40];assert len(raw)==40
  size,start,relptr,lineptr,nrel,nline,characteristics=struct.unpack_from('<IIIIHHI',raw,16);assert start+size<=len(data)
  sections[n]=dict(number=n,size=size,start=start,relocations=nrel,characteristics=characteristics,data=data[start:start+size].hex())
 symbols=[];aux={};n=0
 while n<nsyms:
  off=symoff+n*18;raw=data[off:off+18];nm=name(raw[:8]);value,section,typ,storage,count=struct.unpack_from('<IhHBB',raw,8);assert n+count<nsyms
  symbols.append(dict(name=nm,value=value,section=section,type=typ,storage=storage,aux_count=count,index=n))
  if storage==3 and count==1 and section>0 and value==0 and typ==0:
   a=data[off+18:off+36];length,rel,line,checksum,number,selection,reserved,high=struct.unpack('<IHHIHBBH',a);aux[section]=dict(length=length,relocations=rel,checksum=checksum,selection=selection)
  n+=1+count
 return sections,symbols,aux

def main():
 p=argparse.ArgumentParser();p.add_argument('inventory',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 def read(p):return json.loads(p.read_text(encoding='utf-8'))
 objects=read(a.inventory/'objects.json');dups=read(a.inventory/'duplicate-definitions.json');wanted={x['object'] for rows in dups.values() for x in rows};parsed={};tool=LLVM/'bin/llvm-readobj.exe'
 for n in sorted(wanted):
  obj=objects[n];path=Path('local/compiler-spike')/obj['source_batch']/obj['folder']/'function.obj';assert sha(path)==obj['object_sha256'];data=path.read_bytes();sections,symbols,aux=raw_coff(data)
  r=subprocess.run([str(tool),'--elf-output-style=JSON','--sections','--symbols',str(path)],capture_output=True,timeout=120);assert r.returncode==0;(a.out/f'object-{n:04d}.readobj.txt').write_bytes(r.stdout);(a.out/f'object-{n:04d}.stderr').write_bytes(r.stderr)
  text=r.stdout.decode('utf-8');decoder=json.JSONDecoder()
  # Pinned readobj's COFF JSON printer emits standalone Sections/Symbols
  # objects after a non-JSON file preamble. Parse those exact JSON objects.
  sec=decoder.raw_decode(text[text.index('{"Sections":'):])[0]['Sections'];sym=decoder.raw_decode(text[text.index('{"Symbols":'):])[0]['Symbols']
  parsed[n]=(sections,symbols,aux,{x['Section']['Number']:x['Section'] for x in sec},[x['Symbol'] for x in sym])
 checks=[]
 for name,occurrences in sorted(dups.items()):
  match=re.fullmatch(r'__(real|xmm|ymm)@([0-9a-f]+)',name);assert match,('unexpected duplicated global',name)
  expected=bytes.fromhex(match[2])[::-1].hex();rows=[]
  for item in occurrences:
   assert item['kind']=='R';n=item['object'];sections,symbols,aux,isections,isymbols=parsed[n]
   candidates=[s for s in symbols if s['name']==name];assert len(candidates)==1;s=candidates[0];assert s['storage']==2 and s['value']==0 and s['aux_count']==0
   sec=sections[s['section']];assert sec['data']==expected and sec['relocations']==0 and sec['characteristics']&0x1000 and not sec['characteristics']&0xa0000000 and aux[s['section']]['selection']==2
   independent=next(x for x in isymbols if x['Name']==name);assert independent['Value']==s['value'] and independent['Section']['Value']==s['section'] and independent['StorageClass']['Value']==s['storage']
   isec=isections[s['section']];assert (isec['RawDataSize'],isec['PointerToRawData'],isec['RelocationCount'],isec['Characteristics']['Value'])==(sec['size'],sec['start'],sec['relocations'],sec['characteristics'])
   iaux=next(x['AuxSectionDef'] for x in isymbols if x['Section']['Value']==s['section'] and 'AuxSectionDef' in x);assert iaux['Selection']==dict(Name='Any',Value=2) and iaux['Length']==sec['size']
   rows.append(dict(object=n,section=s['section'],symbol_index=s['index'],data=sec['data'],selection='Any',readobj_sha256=sha(a.out/f'object-{n:04d}.readobj.txt')))
  checks.append(dict(symbol=name,bytes=len(bytes.fromhex(expected)),occurrences=rows))
 result=dict(status='all duplicated globals are matching read-only constant COMDATs',input_sha256={name:sha(a.inventory/name) for name in ['objects.json','duplicate-definitions.json']},llvm_readobj_sha256=sha(tool),duplicate_symbols=len(checks),definitions=sum(len(x['occurrences']) for x in checks),objects=len(wanted),checks=checks,limitations='Independent raw-record and LLVM metadata checks plus exact constant payload equality. This does not link the game or establish any runtime service/ABI behavior.')
 write_json(a.out/'checked.json',result);print(json.dumps({k:result[k] for k in ['status','duplicate_symbols','definitions','objects']}))
if __name__=='__main__':main()
