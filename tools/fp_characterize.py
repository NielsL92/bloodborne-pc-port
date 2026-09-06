"""Characterize authored SIMD results, sticky flags and unmasked native faults."""
import json,subprocess,sys
from pathlib import Path
from tools.dev import ROOT,LLVM,environment
from tools.cfg_recover_startup import sha,write_json
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
operations=[('vminps',None),('vmaxps',None),('vsqrtps',None)]+[('vroundsd',n) for n in range(16)]
assembly=['.intel_syntax noprefix','.text'];header=[]
for n,(op,imm) in enumerate(operations):
 name=f'probe_{n}';site=f'probe_site_{n}';header.extend([f'extern "C" void {name}(const void*,void*);',f'extern "C" char {site};'])
 instruction=f'{op} xmm0, xmm1, xmm2' if op in ('vminps','vmaxps') else 'vsqrtps xmm0, xmm2' if op=='vsqrtps' else f'vroundsd xmm0, xmm1, xmm2, {imm}'
 assembly.extend([f'.globl {name}',name+':','vmovdqu xmm0, xmmword ptr [rcx+32]','vmovdqu xmm1, xmmword ptr [rcx]','vmovdqu xmm2, xmmword ptr [rcx+16]',f'.globl {site}',site+':',instruction,'vmovdqu xmmword ptr [rdx], xmm0','ret'])
header.extend(['static Probe probes[]={'+','.join(f'probe_{n}' for n in range(len(operations)))+'};','static const void* sites[]={'+','.join(f'&probe_site_{n}' for n in range(len(operations)))+'};'])
(out/'probes.s').write_text('\n'.join(assembly)+'\n',encoding='utf-8');(out/'probes.h').write_text('\n'.join(header)+'\n',encoding='utf-8');write_json(out/'operations.json',[dict(operation=op,immediate=imm) for op,imm in operations])
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=120)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'probes.s','-o',out/'probes.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/I'+str(out),'/c',ROOT/'native/semantics/fp_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'probes.obj','/Fe'+str(out/'probe.exe')])
run('execute',[out/'probe.exe']);rows=[json.loads(line) for line in (out/'execute.stdout').open()];assert len(rows)==77824
counts={};flags={}
for r in rows:
 key=f"{r['operation']}:{r['code']:08x}";counts[key]=counts.get(key,0)+1
 key=f"{r['operation']}:{r['control']&0x1f80:04x}:{r['csr']&63:02x}:{r['code']:08x}";flags[key]=flags.get(key,0)+1
write_json(out/'summary.json',dict(status='authored hardware floating-state characterization complete',cases=len(rows),outcomes=counts,flag_outcomes=flags,raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'probe.exe'),limitations='Authored host instructions only. Observation records are inputs to semantic design; no AOT/game correctness or PS4 exception delivery claim.'))
print(json.dumps(dict(cases=len(rows),outcomes=counts)),flush=True)
