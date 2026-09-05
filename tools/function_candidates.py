"""Build a stratified real-code candidate inventory; no execution or correctness claim."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import time
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_GRP_CALL,CS_GRP_JUMP,CS_GRP_RET
from capstone.x86_const import X86_OP_MEM,X86_OP_IMM,X86_REG_RIP
from tools.formats import ElfImage
ROOT=Path(__file__).resolve().parents[1]
def describe(image,fn,decoder):
    code=image.at_va(fn["start"],fn["size"])
    ins=list(decoder.disasm(code,fn["start"]))
    if not ins or sum(i.size for i in ins)!=len(code):
        return None
    calls=[i for i in ins if i.group(CS_GRP_CALL)]
    jumps=[i for i in ins if i.group(CS_GRP_JUMP)]
    memory=[i for i in ins if any(o.type==X86_OP_MEM for o in i.operands)]
    tags=[]
    if memory: tags.append("memory")
    if any("rsp" in i.op_str or "rbp" in i.op_str or i.mnemonic in ("push","pop") for i in ins): tags.append("stack")
    if jumps: tags.append("branches")
    if any(i.operands[0].type==X86_OP_IMM and i.operands[0].imm<=i.address for i in jumps): tags.append("loops")
    if any(i.operands[0].type==X86_OP_IMM for i in calls): tags.append("direct_calls")
    if any(i.operands[0].type!=X86_OP_IMM for i in calls): tags.append("indirect_calls")
    if any(i.operands[0].type!=X86_OP_IMM for i in jumps): tags.append("indirect_jumps")
    if any("xmm" in i.op_str or "ymm" in i.op_str for i in ins): tags.append("simd")
    if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for i in ins for o in i.operands): tags.append("rip_relative")
    outside=[hex(i.operands[0].imm) for i in jumps if i.operands[0].type==X86_OP_IMM and not fn["start"]<=i.operands[0].imm<fn["start"]+fn["size"]]
    return dict(start=fn["start"],size=fn["size"],sha256=hashlib.sha256(code).hexdigest(),
                instructions=len(ins),tags=tags,external_direct_jumps=outside,
                direct_call_targets=[i.operands[0].imm for i in calls if i.operands[0].type==X86_OP_IMM],
                returns=sum(i.group(CS_GRP_RET) for i in ins),
                disassembly=[f"{i.address:x}: {i.mnemonic} {i.op_str}" for i in ins])
def main():
    begin=time.monotonic()
    raw=(ROOT/"local/update/uroot/eboot.bin").read_bytes();image=ElfImage(raw)
    functions=image.unwind_functions(); decoder=Cs(CS_ARCH_X86,CS_MODE_64);decoder.detail=True
    pools=defaultdict(list)
    for fn in functions:
        if 32<=fn["size"]<=384:
            pools["small"].append(fn)
        elif 385<=fn["size"]<=2048:
            pools["medium"].append(fn)
        elif 2049<=fn["size"]<=16384:
            pools["large"].append(fn)
        elif fn["size"]>16384:
            pools["very_large"].append(fn)
    rng=random.Random(0xB100DB02)
    batch=[]
    for name,count in (("small",400),("medium",300),("large",250),("very_large",50)):
        for fn in rng.sample(pools[name],min(count,len(pools[name]))):
            item=describe(image,fn,decoder)
            batch.append(dict(fn,stratum=name,decode=item))
    candidates=defaultdict(list)
    # Bounded scan of small real unwind ranges, with a separate candidate pool per feature.
    for fn in pools["small"]:
        if fn["size"]>200: continue
        item=describe(image,fn,decoder)
        if not item or not item["returns"] or item["instructions"]<8: continue
        if item["external_direct_jumps"]: continue
        for tag in ("memory","loops","simd","direct_calls","indirect_calls","rip_relative"):
            if tag in item["tags"] and len(candidates[tag])<12:
                candidates[tag].append(item)
        if all(len(candidates[t])==12 for t in ("memory","loops","simd","direct_calls","indirect_calls","rip_relative")): break
    out=ROOT/"local/compiler-spike";out.mkdir(parents=True,exist_ok=True)
    data=dict(status="selection_only_not_compiled_or_validated",input_sha256=hashlib.sha256(raw).hexdigest(),
              seed="0xb100db02",elapsed_seconds=time.monotonic()-begin,stratum_populations={k:len(v) for k,v in pools.items()},
              scaling_batch=batch,contract_candidates=candidates)
    (out/"candidates.json").write_text(json.dumps(data,indent=2)+"\n")
    tags=Counter(t for r in batch if r["decode"] for t in r["decode"]["tags"])
    print(json.dumps(dict(batch=len(batch),decode_rejected=sum(r["decode"] is None for r in batch),features=tags,
                          contract_candidates={k:len(v) for k,v in candidates.items()},elapsed_seconds=data["elapsed_seconds"]),indent=2))
if __name__=="__main__": main()
