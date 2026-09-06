"""Characterize x87 tag import/export using authored native control instructions."""
import argparse,json,subprocess
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import ROOT,LLVM,environment
p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);env=environment();steps=[]
assembly='.intel_syntax noprefix\n.text\n.globl probe_env\nprobe_env:\nfxsave64 [r9]\nfxrstor64 [rcx]\nfldenv [rdx]\nfxsave64 [r8]\nfnstenv [r8+512]\nfxrstor64 [r9]\nret\n';(out/'authored.s').write_text(assembly,encoding='utf-8')
def run(name,argv):
 with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:r=subprocess.run(list(map(str,argv)),env=env,stdout=stdout,stderr=stderr,timeout=180)
 steps.append(dict(argv=list(map(str,argv)),exit_code=r.returncode));write_json(out/'steps.json',steps);assert r.returncode==0,name
run('assemble',[LLVM/'bin/clang.exe','-c',out/'authored.s','-o',out/'authored.obj'])
run('fixture',[LLVM/'bin/clang-cl.exe','/nologo','/O2','/EHsc','/std:c++17','/clang:-mno-avx','/c',ROOT/'native/semantics/x87_environment_probe.cpp','/Fo'+str(out/'fixture.obj')])
run('link',[LLVM/'bin/clang-cl.exe','/nologo',out/'fixture.obj',out/'authored.obj','/Fe'+str(out/'fixture.exe')])
run('execute',[out/'fixture.exe'])
rows=[json.loads(line) for line in (out/'execute.stdout').open()];groups=[r for r in rows if r['kind']=='group'];assert len(groups)==32
summary=dict(status='authored x87 tag-environment characterization complete',host=rows[0],cases=sum(r['cases'] for r in groups),counts={key:sum(r[key] for r in groups) for key in ['literal_full_tags','reconstructed_full_tags','abridged_tags','control','top_matches','nonempty_payloads']},groups=groups,raw_sha256=sha(out/'execute.stdout'),fixture_sha256=sha(out/'fixture.exe'),assembly_sha256=sha(out/'authored.s'),source_sha256=sha(ROOT/'native/semantics/x87_environment_probe.cpp'),limitations='Authored host instructions only; all x87 exceptions masked. Raw tag import/export and nonempty payload mapping only; no arithmetic, native guest faults, game CPU execution or PS4 behavior proof. A matching host model still needs manual cross-check and native semantic implementation.')
write_json(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='groups'}),flush=True)
