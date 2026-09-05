"""Compile every undisputed startup manifest in bounded sparse AOT batches.

No game code is linked or executed. Failed batches are split to identify exact
rejected entries. Link ownership, indirect dispatch and native services remain
explicit obligations, including overlapping logical root definitions.
"""
import argparse,collections,concurrent.futures,json,re,sqlite3,subprocess,time
from pathlib import Path
from tools.cfg_recover_startup import sha,write_json
from tools.dev import LLVM,environment
from tools.formats import ElfImage


def partition(units,max_units,max_instructions):
    batches=[];current=[];size=0;module=None
    for u in units:
        n=len(u['instructions'])
        if current and (u['module_sha256']!=module or len(current)>=max_units or size+n>max_instructions):
            batches.append(current);current=[];size=0
        current.append(u);size+=n;module=u['module_sha256']
    if current:batches.append(current)
    return batches


def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('lifter',type=Path)
    p.add_argument('--max-units',type=int,default=128);p.add_argument('--max-instructions',type=int,default=5000)
    p.add_argument('--workers',type=int,default=2);p.add_argument('--sample-batches',type=int,default=0)
    p.add_argument('--entries',type=Path);p.add_argument('--semantics',type=Path);p.add_argument('--explicit-ud2',action='store_true')
    a=p.parse_args();assert a.max_units>0 and a.max_instructions>0 and 1<=a.workers<=2 and a.sample_batches>=0
    a.out.mkdir(parents=True,exist_ok=False);lifter=a.lifter.resolve();env=environment()
    units=[json.loads(line) for line in (a.source/'compilation-manifest.jsonl').open(encoding='utf-8')]
    rejected=[u for u in units if u['issues'] or not u['instructions']]
    selected=[u for u in units if not u['issues'] and u['instructions']]
    if a.entries:
        keys={(r['module'],r['start']) for r in json.loads(a.entries.read_text())}
        assert keys<={(u['module_sha256'],u['entry']) for u in units}, 'requested entry missing'
        selected=[u for u in selected if (u['module_sha256'],u['entry']) in keys]
    semantics=a.semantics.resolve() if a.semantics else Path('build/remill/lib/Arch/X86/Runtime').resolve()
    assert (semantics/'amd64_avx.bc').is_file()
    assert len({(u['module_sha256'],u['entry']) for u in units})==len(units)
    db=sqlite3.connect(f'{(a.source/"analysis.sqlite").resolve().as_uri()}?mode=ro',uri=True)
    modules=sorted(db.execute('SELECT hash,name,path FROM module'),key=lambda r:(r[1]!='eboot.bin',r[1]))
    bases={h:(n+1)*0x100000000 for n,(h,_,_) in enumerate(modules)};images={}
    for h,_,path in modules:
        assert sha(path)==h;images[h]=ElfImage(Path(path).read_bytes())
        assert all(s.vaddr+s.memsz<0x100000000 for s in images[h].segments),'module exceeds reserved logical slot'
    pads=collections.defaultdict(set)
    for h,entry,pad in db.execute('SELECT DISTINCT module,range_start,landing_pad FROM exception_call_site WHERE landing_pad IS NOT NULL'):
        pads[h,entry].add(pad)
    batches=partition(selected,a.max_units,a.max_instructions)
    indices=list(range(len(batches)))
    if a.sample_batches and a.sample_batches<len(batches):
        indices=sorted({i*(len(batches)-1)//max(1,a.sample_batches-1) for i in range(a.sample_batches)})
    plan=[dict(batch=i,module=b[0]['module_sha256'],entries=[u['entry'] for u in b],instructions=sum(len(u['instructions']) for u in b),selected=i in indices) for i,b in enumerate(batches)]
    write_json(a.out/'plan.json',plan);write_json(a.out/'quarantined-manifests.json',rejected)
    write_json(a.out/'identity.json',dict(schema=1,source_db_sha256=sha(a.source/'analysis.sqlite'),source_manifest_sha256=sha(a.source/'compilation-manifest.jsonl'),plan_sha256=sha(a.out/'plan.json'),lifter_sha256=sha(lifter),clang_sha256=sha(LLVM/'bin/clang.exe'),semantics_sha256=sha(semantics/'amd64_avx.bc'),semantics_directory=str(semantics),entry_selection_sha256=sha(a.entries) if a.entries else None,explicit_ud2=a.explicit_ud2,module_mapping=[dict(module=h,name=name,logical_base=bases[h]) for h,name,_ in modules],object_flags=['-O2','-march=haswell','-mno-incremental-linker-compatible'],execution='none',selection='All issue-free entries, module/RVA order; optional evenly-spaced batch pilot; no size/shape exclusions. Single units exceeding the budget stay intact.',runtime_mapping='Experiment assigns one distinct 4-GiB logical slot per module; this does not implement relocation, loading or native binding.'))

    def run(cmd,folder,name):
        start=time.monotonic();error=None;code=None
        with (folder/(name+'.stdout')).open('wb') as o,(folder/(name+'.stderr')).open('wb') as e:
            try:code=subprocess.run(list(map(str,cmd)),env=env,stdout=o,stderr=e,timeout=180).returncode
            except subprocess.TimeoutExpired:error='180-second per-command budget exhausted; child terminated'
        return dict(argv=list(map(str,cmd)),exit_code=code,error=error,elapsed_seconds=time.monotonic()-start)

    def compile_batch(batch,tag):
        folder=a.out/tag;folder.mkdir();h=batch[0]['module_sha256'];base=bases[h];ins={};roots={};edges=[]
        for u in batch:
            assert u['module_sha256']==h
            for i in u['instructions']:
                pc=i['rva'];raw=i['bytes'];assert len(bytes.fromhex(raw))==i['size'] and images[h].at_va(pc,i['size']).hex()==raw
                assert pc not in ins or ins[pc]==raw;ins[pc]=raw
            roots[u['entry']]='manifest entry';edges.extend(u['edges'])
            for pad in pads[h,u['entry']]:
                assert any(i['rva']==pad for i in u['instructions']);roots.setdefault(pad,'LSDA landing pad')
        for edge in edges:
            if edge['target_module']==h and edge['target'] in ins and edge['kind'] in ('validated_jump_table','independently_recovered_jump_table','direct_call'):
                roots.setdefault(edge['target'],'explicit recovered target '+edge['kind'])
        data=dict(roots=[base+pc for pc in sorted(roots)],instructions=[dict(address=base+pc,bytes=raw) for pc,raw in sorted(ins.items())])
        if a.explicit_ud2:
            traps={e['source'] for e in edges if e['kind']=='service_or_trap_boundary' and e['detail']=='ud2'}
            assert all(ins.get(pc)=='0f0b' for pc in traps)
            data['native_traps']=[dict(address=base+pc,kind='ud2') for pc in sorted(traps)]
        write_json(folder/'input.json',data);write_json(folder/'roots.json',[dict(rva=pc,reason=why) for pc,why in sorted(roots.items())])
        write_json(folder/'units.json',[dict(entry=u['entry'],constructor_ordinal=u['constructor_ordinal'],instruction_set_sha256=u['instruction_set_sha256']) for u in batch])
        result=dict(folder=tag,module=h,entries=[u['entry'] for u in batch],instructions=len(ins),roots=len(roots),input_sha256=sha(folder/'input.json'),execution='not_executed')
        result['lift']=run([lifter,folder/'input.json',folder/'function.bc',folder/'function.ll',folder/'audit.json',*([semantics] if a.semantics else [])],folder,'lift');result['status']='lift_rejected'
        if result['lift']['exit_code']==0:
            audit=json.loads((folder/'audit.json').read_text());assert set(audit['decoded_addresses'])=={base+pc for pc in ins} and not audit['unvisited_manifest_instructions']
            assert set(audit['compiled_roots'])==set(data['roots'])
            ir=(folder/'function.ll').read_text();result['external_declarations']=re.findall(r'^declare[^@]*@([^ (]+)',ir,re.M)
            result['explicit_native_trap_addresses']=audit.get('explicit_native_trap_addresses',[]);result['semantic_instruction_count']=audit.get('semantic_instruction_count',len(ins));
            result['missing_instruction_starts']=audit['missing_instruction_starts'];result['compiled_roots']=audit['compiled_roots'];result['audit_sha256']=sha(folder/'audit.json')
            result['compile']=run([LLVM/'bin/clang.exe','-c','-O2','-march=haswell','-mno-incremental-linker-compatible',folder/'function.bc','-o',folder/'function.obj'],folder,'compile')
            result['status']='object_built' if result['compile']['exit_code']==0 else 'object_failed'
            if result['status']=='object_built':result.update(object_sha256=sha(folder/'function.obj'),object_bytes=(folder/'function.obj').stat().st_size)
        if result['status']!='object_built' and len(batch)>1:
            result['status']='split_rejected_batch';write_json(folder/'result.json',result)
            cut=len(batch)//2
            leaves=compile_batch(batch[:cut],tag+'-a')+compile_batch(batch[cut:],tag+'-b')
            return leaves
        write_json(folder/'result.json',result)
        print(json.dumps(dict(batch=tag,entries=len(batch),instructions=len(ins),status=result['status'])),flush=True)
        return [result]

    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures={pool.submit(compile_batch,batches[i],f'batch-{i:04d}'):i for i in indices}
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result());write_json(a.out/'progress.json',dict(finished_units=sum(len(r['entries']) for r in results),finished_objects=sum(r['status']=='object_built' for r in results)))
    results.sort(key=lambda r:r['folder']);write_json(a.out/'results.json',results)
    root_owners=collections.defaultdict(list)
    for r in results:
        if r['status']=='object_built':
            for pc in r['compiled_roots']:root_owners[pc].append(r['folder'])
    duplicates=[dict(logical_pc=pc,objects=owners) for pc,owners in sorted(root_owners.items()) if len(owners)>1]
    write_json(a.out/'duplicate-root-owners.json',duplicates)
    built={entry for r in results if r['status']=='object_built' for entry in ((r['module'],pc) for pc in r['entries'])}
    constructors={u['entry'] for u in units if u['constructor_ordinal'] is not None}
    main=modules[0][0];assert modules[0][1]=='eboot.bin'
    summary=dict(status='bounded sparse compilation survey complete; startup gate NOT passed',manifest_units=len(units),quarantined_units=len(rejected),planned_batches=len(batches),selected_batches=len(indices),selected_units=sum(len(batches[i]) for i in indices),compiled_units=len(built),compiled_constructors=sum((main,pc) in built for pc in constructors),constructor_entries=len(constructors),results=dict(collections.Counter(r['status'] for r in results)),object_bytes=sum(r.get('object_bytes',0) for r in results),duplicate_logical_roots=len(duplicates),missing_path_records=sum(len(r.get('missing_instruction_starts',[])) for r in results),explicit_native_trap_sites=sum(len(r.get('explicit_native_trap_addresses',[])) for r in results),limitations='All objects are static compilation evidence. Explicit indirect/service/exception/callback boundaries and logical-root ownership require native runtime/link integration. No game linking/execution, original CPU fallback or performance claim.')
    write_json(a.out/'summary.json',summary);print(json.dumps(summary),flush=True)
    raise SystemExit(any(r['status']!='object_built' for r in results))

if __name__=='__main__':main()
