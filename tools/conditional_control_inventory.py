"""Bounded disputed-ending proof with explicit ordinary-call obligations at three sites.

This does not change the generic derivation policy. It never resolves an indirect
call target, validates a saved continuation, or declares the P3 gate complete.
"""
import argparse,collections,copy,json,sqlite3
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from tools.cfg_recover_startup import sha,write_json
from tools.cfg_derive_control import model_nodes,prove
from tools.startup_service_inventory import MAIN,LIBC
HELPERS=((MAIN,0x210ad70),(LIBC,0x60750),(LIBC,0x60560))
CALLBACKS={(MAIN,0x210ad70):{0x210ad84:'ff5050'},(LIBC,0x60750):{0x60811:'ff5110',0x6081f:'ff5110'}}
SITES=((LIBC,0x60510,0x60541,0x60560),(LIBC,0x60560,0x605d9,0x60750),(LIBC,0x606f0,0x60742,0x60750),(MAIN,0x210b0e0,0x210b72b,0x210ad70),(MAIN,0x210b940,0x210b9e0,0x210ad70))
CONDITIONS=['Each listed unresolved indirect CALL either returns to its explicit next instruction under the ordinary SysV call/return contract, or transfers nonlocally/terminates through an explicit native boundary. The actual target and all nonlocal destinations remain unvalidated.','The stated direct/import terminal contracts hold; their native service, callback, saved-context and exception implementations remain open.','Code and saved control state satisfy the stated compilation/ABI contract. Arbitrary callback stack/code corruption, asynchronous transfers and missing exception paths are not validated by this conditional summary.']
def model(unit,known_local,known_import,allow_callbacks):
 h=unit['module_sha256'];rows=[(i['rva'],i['size'],i['bytes'],i['mnemonic']) for i in unit['decoded']];edges=collections.defaultdict(list);approved=CALLBACKS.get((h,unit['entry']),{}) if allow_callbacks else {}
 for e in unit['edges']:
  if e['kind']=='unresolved_indirect_call' and e['source'] in approved:continue
  if e['kind']=='annotated_control_contract_requires_runtime':continue # reconstruct from verified base/local bindings instead
  edges[e['source']].append((e['target_module'],e['target'],e['kind'],e['detail']))
 for pc,b in approved.items():
  i=next(i for i in unit['decoded'] if i['rva']==pc);assert i['bytes']==b and i['mnemonic']=='call'
  assert any(e['source']==pc and e['kind']=='unresolved_indirect_call' for e in unit['edges'])
  assert [e['target'] for e in unit['edges'] if e['source']==pc and e['kind']=='fallthrough']==[pc+i['size']]
 return model_nodes(h,rows,edges,known_local,known_import)
def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 identity=json.loads((a.source/'identity.json').read_text(encoding='utf-8'));base_path=Path('tools/cfg_import_contracts.json');assert identity['control_contracts_sha256']==sha(base_path);base=json.loads(base_path.read_text(encoding='utf-8'))
 known_local={(e['module_sha256'],e['rva']):[c['id']] for c in base['contracts'] for e in c.get('local_entries',[])};known_import={tuple(c[k] for k in ('nid','library','module')):[c['id']] for c in base['contracts']}
 selected=set(HELPERS)|{(h,e) for h,e,pc,t in SITES};units={};decoder=Cs(CS_ARCH_X86,CS_MODE_64)
 for line in (a.source/'compilation-manifest.jsonl').open(encoding='utf-8'):
  u=json.loads(line);key=(u['module_sha256'],u['entry'])
  if key not in selected:continue
  u['decoded']=[]
  for i in u['instructions']:
   dec=list(decoder.disasm(bytes.fromhex(i['bytes']),i['rva']));assert len(dec)==1 and dec[0].size==i['size'];u['decoded'].append(i|dict(mnemonic=dec[0].mnemonic,operands=dec[0].op_str))
  units[key]=u
 assert set(units)==selected
 db=sqlite3.connect((a.source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
 for (h,e),u in units.items():
  u['roots']=[e]+[r[0] for r in db.execute('SELECT DISTINCT landing_pad FROM exception_call_site WHERE module=? AND range_start=? AND landing_pad IS NOT NULL ORDER BY landing_pad',(h,e))]
  full_edges=[dict(source=pc,target_module=other,target=dst,kind=kind,detail=detail) for pc,other,dst,kind,detail in db.execute('SELECT source,target_module,target,kind,detail FROM recovery_edge WHERE module=? AND entry=? ORDER BY source,kind,target',(h,e))]
  assert [edge for edge in full_edges if edge['kind']!='fallthrough']==u['edges']
  u['edges']=full_edges # Compilation manifests intentionally omit ordinary fallthrough.
 proofs={};strict_rejections=[]
 for iteration in range(3):
  changed=False
  for key in HELPERS:
   if key in proofs:continue
   u=units[key];nodes,terminals,evidence=model(u,known_local,known_import,False);strict=prove(nodes,u['roots'],terminals)
   nodes,terminals,evidence=model(u,known_local,known_import,True);visited=prove(nodes,u['roots'],terminals)
   if visited is None:continue
   assert visited==[i['rva'] for i in u['instructions']],'proof did not account for complete current helper instruction set'
   ident='conditional-callback-control-'+key[0][:12]+'-'+format(key[1],'x');used={str(pc):evidence[pc] for pc in visited if pc in terminals}
   callbacks=[dict(site=pc,bytes=b,obligation=CONDITIONS[0]) for pc,b in CALLBACKS.get(key,{}).items()]
   proof=dict(id=ident,module=key[0],entry=key[1],roots=u['roots'],terminals=used,dependencies=sorted({c for cs in used.values() for c in cs}),callbacks=callbacks,visited=visited,iteration=iteration,strict_generic_model_passed=strict is not None)
   proofs[key]=proof;known_local[key]=[ident];changed=True
  if not changed:break
 assert set(proofs)==set(HELPERS),[(h,hex(e)) for h,e in set(HELPERS)-set(proofs)]
 sites=[]
 for h,e,pc,target in SITES:
  u=units[h,e];assert len(u['issues'])==1 and u['issues'][0]['rva']==pc and u['issues'][0]['kind']=='fallthrough_at_fence'
  ins=next(i for i in u['decoded'] if i['rva']==pc);assert ins['mnemonic']=='call'
  assert any(x['source']==pc and x['target']==target and x['kind']=='direct_call' for x in u['edges'])
  sites.append(dict(module=h,entry=e,site=pc,target=target,id='disputed-ending-'+h[:12]+'-'+format(e,'x'),proof_id=proofs[h,target]['id']))
 r=dict(status='conditional callback-control proposal; independent check pending',source=str(a.source),source_db_sha256=sha(a.source/'analysis.sqlite'),source_manifest_sha256=sha(a.source/'compilation-manifest.jsonl'),base_contracts_sha256=sha(base_path),base_contracts=base,proofs=list(proofs.values()),sites=sites,units=list(units.values()),conditions=CONDITIONS,limitations=['Exactly five disputed ending sites only; do not install these as global function or import summaries.','Generic cfg_derive_control remains strict about all unknown calls. The three named CALL sites gain explicit conditional ordinary-call obligations in this separate proof only.','No unknown call, callback target, saved continuation, constructor-table mutation or native execution gate is closed by this proposal.'],evidence={str(p):sha(p) for p in [base_path,Path('local/cfg/lua-panic-checked-v1/checked.json'),Path('local/cfg/exception-rtti-checked-v2-provenance/checked.json')]})
 write_json(a.out/'proposal.json',r);write_json(a.out/'selection.json',[dict(module=h,start=e,reason='independent disputed ending and conditional callback-control check') for h,e in sorted(selected)])
 print(json.dumps(dict(status=r['status'],helpers=len(proofs),sites=len(sites),callback_sites=sum(len(p['callbacks']) for p in proofs.values()),strict_model={hex(p['entry']):p['strict_generic_model_passed'] for p in proofs.values()})))
if __name__=='__main__':main()
