"""Independently reslice earlier cache addresses and verify dispatch tail operands."""
import argparse,collections,json,re,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.check_dispatch_cohort import match_cached_tail
root=Path.cwd();p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('slices',type=Path);p.add_argument('ghidra',type=Path);p.add_argument('out',type=Path);a=p.parse_args();source,slices,ghidra,out=a.source.resolve(),a.slices,a.ghidra,a.out;out.mkdir(parents=True,exist_ok=False)

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def reg(name):
 name=name.lower();aliases={'eax':'rax','ax':'rax','al':'rax','ah':'rax','ebx':'rbx','bx':'rbx','bl':'rbx','bh':'rbx','ecx':'rcx','cx':'rcx','cl':'rcx','ch':'rcx','edx':'rdx','dx':'rdx','dl':'rdx','dh':'rdx','edi':'rdi','di':'rdi','dil':'rdi','esi':'rsi','si':'rsi','sil':'rsi','ebp':'rbp','bp':'rbp','bpl':'rbp','esp':'rsp','sp':'rsp','spl':'rsp'}
 if re.fullmatch(r'r\d+[bwd]',name):return name[:-1]
 return aliases.get(name,name)
con=sqlite3.connect((source/'analysis.sqlite').as_uri()+'?mode=ro',uri=True);names=dict(con.execute('select hash,name from module'));raw={};checked=[]
for original in read(slices/'slices.json'):
 h,entry=original['module'],original['entry']
 if h not in raw:raw[h]={r['start']:r for r in read(ghidra/names[h]/'ghidra.json')}
 window=raw[h][entry];ins={r['rva']:r for r in window['instructions']};pred=collections.defaultdict(set)
 terminal={r[0] for r in con.execute("select source from recovery_edge where module=? and entry=? and kind='annotated_control_contract_requires_runtime'",(h,entry))}
 for pc,i in ins.items():
  flow=i['flow']
  if 'JUMP' in flow:
   for target in i['targets']:
    if target in ins:pred[target].add(pc)
  if pc not in terminal and flow not in ('UNCONDITIONAL_JUMP','COMPUTED_JUMP') and 'TERMINATOR' not in flow and pc+i['length'] in ins:pred[pc+i['length']].add(pc)
 for row in original['source_instructions']:
  assert row['pc'] in ins and (row['size'],row['bytes'])==(ins[row['pc']]['length'],ins[row['pc']]['bytes'])
 seen=set();evidence=set();failures=set();assumptions=set();targets=set();graph={};pending=collections.deque([(original['site'],original['contract']['register'])])
 while pending:
  key=pending.popleft();point,register=key
  if key in seen:continue
  if len(seen)>=2048:failures.add(('budget',point,register));continue
  seen.add(key);graph[key]=set()
  if point in original['roots']:failures.add(('entry-register',point,register));continue
  if not pred.get(point):failures.add(('missing-predecessor',point,register));continue
  def link(parent,value):
   child=(parent,value);graph[key].add(child);pending.append(child)
  for pc in sorted(pred[point]):
   i=ins[pc];evidence.add(pc)
   if 'CALL' in i['flow']:
    if register not in ('rbx','rbp','r12','r13','r14','r15'):failures.add(('volatile-call-result',pc,register))
    else:assumptions.add(pc);link(pc,register)
    continue
   if register not in {reg(r) for r in i['written_registers']}:link(pc,register);continue
   text=i['text'];parts=text.split(' ',1);op=parts[0];operands=parts[1].split(',') if len(parts)>1 else [];operands=[p.strip() for p in operands]
   if len(operands)==2 and reg(operands[0])==register:
    dst,src=operands;wide=dst.lower()==register;dword=dst.startswith('E') or bool(re.fullmatch(r'R\d+D',dst))
    if not (wide or dword):failures.add(('partial-write',pc,register));continue
    if op=='MOV':
     if re.fullmatch(r'0x[0-9a-fA-F]+',src):targets.add(('absolute',int(src,16)&((1<<(64 if wide else 32))-1)));continue
     if wide and re.fullmatch(r'R(?:[ABCD]X|[DS]I|[BS]P|[89]|1[0-5])',src):link(pc,reg(src));continue
    if op in ('XOR','SUB') and dst==src:targets.add(('absolute',0));continue
    absolute=re.fullmatch(r'\[0x([0-9a-fA-F]+)\]',src)
    if op=='LEA' and wide and absolute:targets.add(('module-rva',int(absolute[1],16)));continue
   failures.add(('unknown-write',pc,register))
 color={}
 for origin in sorted(graph):
  if color.get(origin):continue
  color[origin]=1;stack=[(origin,iter(sorted(graph[origin])))]
  while stack:
   node,children=stack[-1];child=next(children,None)
   if child is None:color[node]=2;stack.pop();continue
   if child not in graph:continue
   if color.get(child)==1:failures.add(('cycle',child[0],child[1]));continue
   if not color.get(child):color[child]=1;stack.append((child,iter(sorted(graph[child]))))
 independent=dict(complete=not failures,targets=[dict(kind=k,value=v) for k,v in sorted(targets)],failures=[dict(reason=r,pc=p,register=g) for r,p,g in sorted(failures)],instructions=sorted(evidence),conditional_normal_sysv_returns=sorted(assumptions))
 for key in independent:assert independent[key]==original[key],(key,independent[key],original[key])
 independent_tail=match_cached_tail([ins[pc] for pc in original['tail_pcs']]);assert independent_tail==original['tail'],(independent_tail,original['tail'])
 checked.append(dict(**original,independent=independent,independent_instructions=[ins[pc] for pc in sorted(evidence)]))
report=dict(status='independent dispatch cache slices passed',source_db_sha256=sha(source/'analysis.sqlite'),slice_sha256=sha(slices/'slices.json'),ghidra_raw_sha256={names[h]:sha(ghidra/names[h]/'ghidra.json') for h in raw},records=checked,limitations='Independent instruction identities, normal control predecessors, register writes and constant operands agree. Metadata entry roots and explicit nonreturn/normal SysV return contracts remain shared assumptions. This proves conditional cache-address provenance only; no initial or mutable cache value is assumed. No game execution.')
write_json(out/'checked.json',report);print(json.dumps(dict(status=report['status'],records=len(checked),complete=sum(r['complete'] for r in checked),targets=[r['targets'] for r in checked])),flush=True)
