"""Independently reslice callback registers from SLEIGH text, write sets and flow."""
import collections,json,re,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();source=root/'local/cfg/startup-recovery-v13-repeat';slices=root/'local/cfg/callback-slices-v1';ghidra=root/'local/cfg/ghidra-callback-slices-v1';out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
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
 active=set();seen=set();evidence=set();failures=set();assumptions=set()
 def before(pc,register):
  key=(pc,register)
  if key in active:failures.add(('cycle',pc,register));return set()
  if len(seen)>2048:failures.add(('budget',pc,register));return set()
  seen.add(key)
  if pc in original['roots']:failures.add(('entry-register',pc,register));return set()
  if not pred.get(pc):failures.add(('missing-predecessor',pc,register));return set()
  active.add(key);result=set()
  for parent in pred[pc]:result|=after(parent,register)
  active.remove(key);return result
 def after(pc,register):
  i=ins[pc];evidence.add(pc)
  if 'CALL' in i['flow']:
   if register not in ('rbx','rbp','r12','r13','r14','r15'):failures.add(('volatile-call-result',pc,register));return set()
   assumptions.add(pc);return before(pc,register)
  if register not in {reg(r) for r in i['written_registers']}:return before(pc,register)
  text=i['text'];parts=text.split(' ',1);op=parts[0];operands=parts[1].split(',') if len(parts)>1 else [];operands=[p.strip() for p in operands]
  if len(operands)==2 and reg(operands[0])==register:
   dst,src=operands;wide=dst.lower()==register;dword=dst.startswith('E') or bool(re.fullmatch(r'R\d+D',dst))
   if not (wide or dword):failures.add(('partial-write',pc,register));return set()
   if op=='MOV':
    if re.fullmatch(r'0x[0-9a-fA-F]+',src):return {('absolute',int(src,16)&((1<<(64 if wide else 32))-1))}
    if wide and re.fullmatch(r'R(?:[ABCD]X|[DS]I|[BS]P|[89]|1[0-5])',src):return before(pc,reg(src))
   if op in ('XOR','SUB') and dst==src:return {('absolute',0)}
   absolute=re.fullmatch(r'\[0x([0-9a-fA-F]+)\]',src)
   if op=='LEA' and wide and absolute:return {('module-rva',int(absolute[1],16))}
  failures.add(('unknown-write',pc,register));return set()
 targets=before(original['site'],original['contract']['register']);independent=dict(complete=not failures,targets=[dict(kind=k,value=v) for k,v in sorted(targets)],failures=[dict(reason=r,pc=p,register=g) for r,p,g in sorted(failures)],instructions=sorted(evidence),conditional_normal_sysv_returns=sorted(assumptions))
 for key in independent:assert independent[key]==original[key],(key,independent[key],original[key])
 checked.append(dict(**original,independent=independent,independent_instructions=[ins[pc] for pc in sorted(evidence)]))
report=dict(status='independent callback slices passed',source_db_sha256=sha(source/'analysis.sqlite'),slice_sha256=sha(slices/'slices.json'),ghidra_raw_sha256={names[h]:sha(ghidra/names[h]/'ghidra.json') for h in raw},records=checked,limitations='Independent instruction identities, normal control predecessors, register writes and constant operands agree. Metadata entry roots and explicit nonreturn/normal SysV return contracts remain shared assumptions. Entry-provided finalizer is not assigned an invented value. No game execution.')
write_json(out/'checked.json',report);print(json.dumps(dict(status=report['status'],records=len(checked),complete=sum(r['complete'] for r in checked),targets=[r['targets'] for r in checked])),flush=True)
