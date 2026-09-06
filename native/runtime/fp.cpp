// SPDX-License-Identifier: GPL-2.0-or-later
// Explicit per-thread FP profile and exact instruction metadata; no host inference.
#include "runtime.h"
#include <algorithm>
#include <stdexcept>
namespace bb_runtime {
void validate_fp_profile(const FpProfile& p){
 if(!p.identity||!*p.identity||!p.mxcsr_mask||(p.mxcsr_mask&~0xffffu)||(p.image_policy&0xffffffc0ULL)||uint32_t(p.image_policy>>32)!=p.mxcsr_mask||(p.site_count&&!p.sites))throw std::runtime_error("invalid explicit FP profile");
 for(size_t i=0;i<p.site_count;++i)if((i&&p.sites[i-1].pc>=p.sites[i].pc)||p.sites[i].fop>0x7ff||unsigned(p.sites[i].data_segment)>unsigned(Segment::GS))throw std::runtime_error("invalid x87 instruction metadata");
}
static const FpProfile& profile(Memory* m,State* s)noexcept{context(m,s);if(!m->fp_profile)fault(m,"unconfigured-fp-profile",40,s->gpr.rip.qword);return *m->fp_profile;}
static uint16_t selector(State* s,Segment segment)noexcept{
 switch(segment){case Segment::ES:return s->seg.es.flat;case Segment::CS:return s->seg.cs.flat;case Segment::SS:return s->seg.ss.flat;case Segment::DS:return s->seg.ds.flat;case Segment::FS:return s->seg.fs.flat;case Segment::GS:return s->seg.gs.flat;default:return 0;}
}
}
extern "C" uint64_t __bb_native_x87_image_policy(Memory* m,State* s)noexcept{return bb_runtime::profile(m,s).image_policy;}
extern "C" uint32_t __bb_native_mxcsr_mask(Memory* m,State* s)noexcept{return bb_runtime::profile(m,s).mxcsr_mask;}
extern "C" uint32_t __bb_native_x87_pointer_segments(Memory* m,State* s)noexcept{bb_runtime::profile(m,s);return m->pointer_segments;}
extern "C" void __bb_native_x87_set_pointer_segments(Memory* m,State* s,uint32_t value)noexcept{bb_runtime::profile(m,s);m->pointer_segments=value;}
extern "C" void __bb_native_x87_record_instruction(Memory* m,State* s,uint64_t pc,uint32_t flags,uint64_t address)noexcept{
 const auto& p=bb_runtime::profile(m,s);const bb_runtime::X87Site* site=nullptr;
 if(p.site_count){auto* end=p.sites+p.site_count;auto* it=std::lower_bound(p.sites,end,pc,[](const bb_runtime::X87Site& row,uint64_t at){return row.pc<at;});if(it!=end&&it->pc==pc)site=it;}
 if(!site)bb_runtime::fault(m,"unknown-x87-site",41,pc,flags,0,address);
 unsigned pending=(s->sw.ie|(s->sw.de<<1)|(s->sw.ze<<2)|(s->sw.oe<<3)|(s->sw.ue<<4)|(s->sw.pe<<5))&~s->x87.fxsave.cwd.flat&63;
 bool memory=site->data_segment!=bb_runtime::Segment::None,update=memory&&(!(p.image_policy&4)||pending);uint32_t expected=uint32_t(memory)|(uint32_t(update)<<1);
 if(flags!=expected||s->x87.fxsave.ip!=pc||((!(p.image_policy&8)||pending)&&s->x87.fxsave.fop!=site->fop)||(update&&s->x87.fxsave.dp!=address)||(!memory&&address))bb_runtime::fault(m,"x87-metadata-contract",41,pc,flags,expected,address);
 m->pointer_segments=(m->pointer_segments&0xffff0000u)|s->seg.cs.flat;
 if(update)m->pointer_segments=(m->pointer_segments&0xffffu)|(uint32_t(bb_runtime::selector(s,site->data_segment))<<16);
}
extern "C" void __bb_native_x87_check_span(Memory* m,State* s,uint64_t address,uint32_t size,uint32_t write,uint32_t alignment)noexcept{
 bb_runtime::context(m,s);if(write>1)bb_runtime::fault(m,"x87-span-contract",42,s->gpr.rip.qword,write,1,address,size);m->space->check(m,address,size,write!=0,alignment);
}
extern "C" [[noreturn]] void __bb_native_divide_fault(Memory* m,State* s,uint32_t kind,uint32_t width)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"integer-divide",43,s->gpr.rip.qword,kind,0,0,width);}
extern "C" [[noreturn]] void __bb_native_mxcsr_fault(Memory* m,State* s,uint32_t value,uint32_t invalid)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"mxcsr-reserved-bits",44,s->gpr.rip.qword,value,invalid);}
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory* m,State* s,uint32_t raised,uint32_t unmasked)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"simd-unmasked",45,s->gpr.rip.qword,raised,unmasked);}
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory* m,State* s,uint32_t pending)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"x87-pending",46,s->gpr.rip.qword,pending);}
extern "C" [[noreturn]] void __bb_native_x87_unsupported(Memory* m,State* s,uint32_t kind)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"x87-unsupported",47,s->gpr.rip.qword,kind);}
