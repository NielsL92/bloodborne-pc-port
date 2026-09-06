"""Inventory exact remaining x87/MMX startup sites without promoting semantics."""
import collections,json,re,sqlite3,sys
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
root=Path.cwd();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);source=root/'local/cfg/startup-recovery-v22-cache-repeat'
c=sqlite3.connect((source/'analysis.sqlite').resolve().as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
x87=[dict(r) for r in c.execute("select * from recovery_instruction where mnemonic like 'f%' or mnemonic in ('wait','emms') order by module,rva")]
mmx=[dict(r) for r in c.execute("select * from recovery_instruction where operands like '%mm%' or mnemonic in ('emms','femms') order by module,rva") if re.search(r'(?<![a-zA-Z0-9_])mm[0-7](?![a-zA-Z0-9_])',r['operands']) or r['mnemonic'] in ['emms','femms']]
checked={'fld','fldz','fld1','fstp','fxch','fucomi','fucomip','fucompi','fisttp','fild','fchs','fcmovne','fnstcw','fldcw','fnstenv','fldenv','wait','fxsave','fxsave64','fst','fnstsw','fninit'}
for r in x87:
 if r['mnemonic']=='fucompi':assert len(bytes.fromhex(r['bytes']))==2 and bytes.fromhex(r['bytes'])[0]==0xdf and 0xe8<=bytes.fromhex(r['bytes'])[1]<=0xef
remaining=[r for r in x87 if r['mnemonic'] not in checked and r['mnemonic'] not in ['emms','femms']]
selected={(r['module'],r['rva']):r for r in remaining+mmx}
for module in sorted({m for m,_ in selected}):
 addresses=[rva for m,rva in selected if m==module];owners=collections.defaultdict(list)
 for row in c.execute('select rva,entry from recovery_owner where module=? and rva in ('+','.join('?' for _ in addresses)+') order by rva,entry',[module,*addresses]):owners[row['rva']].append(row['entry'])
 for rva in addresses:selected[module,rva]['owners']=owners[rva]
write_json(out/'x87-sites.json',x87);write_json(out/'remaining-arithmetic.json',remaining);write_json(out/'mmx-sites.json',mmx)
summary=dict(status='exact current startup x87/MMX inventory retained; no semantics promoted',source=source.relative_to(root).as_posix(),database_sha256=sha(source/'analysis.sqlite'),manifest_sha256=sha(source/'compilation-manifest.jsonl'),x87_sites=len(x87),x87_mnemonics=dict(collections.Counter(r['mnemonic'] for r in x87)),remaining_sites=len(remaining),remaining_mnemonics=dict(collections.Counter(r['mnemonic'] for r in remaining)),remaining_owners=sorted({(r['module'],entry) for r in remaining for entry in r['owners']}),mmx_sites=len(mmx),mmx_mnemonics=dict(collections.Counter(r['mnemonic'] for r in mmx)),mmx_owners=sorted({(r['module'],entry) for r in mmx for entry in r['owners']}),limitations=['Static recovered graph only; no execution coverage or completeness claim.','Family-level experimental classification does not replace exact selector/instruction manifests or promote checked modules.','No absence claim extends to unknown indirect/callback targets, unvisited paths or later gameplay. MMX/x87 aliasing still needs an explicit runtime contract if MMX reaches the graph.'])
write_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
