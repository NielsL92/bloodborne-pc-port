"""Compile unmodified Lua headers for two data models; execute neither library nor probe."""
import argparse,json,re,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM
p=argparse.ArgumentParser();p.add_argument('reference',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
identity=json.loads((a.reference/'identity.json').read_text(encoding='utf-8'))
for file,digest in identity['files'].items():assert sha(a.reference/file)==digest
source=a.reference/'lua-5.0.2';probe=a.out/'layout.c'
probe.write_text('#include "lstate.h"\n#define OFF(T,F) __builtin_offsetof(T,F)\nconst unsigned long long lua_layout[] = {sizeof(void*),sizeof(long),sizeof(lua_State),sizeof(global_State),sizeof(CallInfo),sizeof(TObject),OFF(lua_State,l_G),OFF(lua_State,errorJmp),OFF(global_State,panic),OFF(lua_State,base_ci),OFF(lua_State,_gt),OFF(global_State,GCthreshold),OFF(global_State,nblocks)};\n',encoding='utf-8')
labels=['pointer_bytes','long_bytes','lua_State_bytes','global_State_bytes','CallInfo_bytes','TObject_bytes','L_l_G','L_errorJmp','G_panic','L_base_ci','L_globals','G_GCthreshold','G_nblocks'];results=[]
for target in ('x86_64-unknown-freebsd','x86_64-pc-windows-msvc'):
 output=a.out/(target+'.ll');cmd=[str(LLVM/'bin/clang.exe'),'--target='+target,'-ffreestanding','-nostdlibinc','-S','-emit-llvm','-O0','-fno-ident','-I',str(source/'include'),'-I',str(source/'src'),str(probe),'-o',str(output)]
 r=subprocess.run(cmd,capture_output=True);(a.out/(target+'.stdout')).write_bytes(r.stdout);(a.out/(target+'.stderr')).write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode(errors='replace')
 ir=output.read_text(encoding='utf-8');line=next(line for line in ir.splitlines() if line.startswith('@lua_layout ='));values=list(map(int,re.findall(r'i64 ([0-9]+)',line)));assert len(values)==len(labels)
 results.append(dict(target=target,layout=dict(zip(labels,values)),argv=cmd,ir_sha256=sha(output)))
lp,llp=[x['layout'] for x in results];assert lp['long_bytes']==8 and lp['L_l_G']==0x20 and lp['L_errorJmp']==0x90 and lp['G_panic']==0x50
assert llp['long_bytes']==4 and llp['G_panic']!=lp['G_panic']
write_json(a.out/'summary.json',dict(status='independent Lua header layout comparison passed',reference_identity_sha256=sha(a.reference/'identity.json'),archive_sha256=identity['sha256'],clang_sha256=sha(LLVM/'bin/clang.exe'),probe_sha256=sha(probe),results=results,execution='none',limitations='Unmodified public Lua 5.0.2 headers under explicit Clang data models. LP64 offsets match the supplied accesses; this does not prove all supplied Lua code/configuration or validate any runtime object. Windows LLP64 is a distinguishing comparison, not a proposed replacement. No jmp_buf definition is inferred from host headers.'))
print(json.dumps(dict(status='layout comparison passed',results=[dict(target=x['target'],layout=x['layout']) for x in results])))
