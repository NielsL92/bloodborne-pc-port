// SPDX-License-Identifier: Apache-2.0
// Experimental integer x87 stack/control semantics. Not the accepted startup module.
// BB_REPLACE_SELECTOR: FLD1
// BB_REPLACE_SELECTOR: FLDZ
// BB_REPLACE_SELECTOR: FNINIT
// BB_REPLACE_SELECTOR: FLDCW_MEMmem16
// BB_REPLACE_SELECTOR: FNSTCW_MEMmem16
// BB_REPLACE_SELECTOR: FNSTSW_MEMmem16
// BB_REPLACE_SELECTOR: FNSTSW_AX
// BB_REPLACE_SELECTOR: FXCH_ST0_X87
// BB_REPLACE_SELECTOR: FXCH_ST0_X87_DFC1
// BB_REPLACE_SELECTOR: FXCH_ST0_X87_DDC1
// BB_REPLACE_SELECTOR: FSTP_X87_ST0
// BB_REPLACE_SELECTOR: FSTP_X87_ST0_DFD0
// BB_REPLACE_SELECTOR: FSTP_X87_ST0_DFD1
// BB_REPLACE_SELECTOR: FUCOMI_ST0_X87
// BB_REPLACE_SELECTOR: FUCOMIP_ST0_X87
// BB_REPLACE_SELECTOR: FWAIT
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory*,State*,uint32_t);
extern "C" uint64_t __bb_native_x87_image_policy(Memory*,State*);
extern "C" void __bb_native_x87_record_instruction(Memory*,State*,addr_t,uint32_t,addr_t);
extern "C" void __bb_native_x87_set_pointer_segments(Memory*,State*,uint32_t);
namespace {
struct __attribute__((packed)) BBX87Bits {uint64_t significand;uint16_t sign_exponent;};
ALWAYS_INLINE BBX87Bits BBX87Read(const float80_t* p){BBX87Bits v;__builtin_memcpy(&v,p,10);return v;}
ALWAYS_INLINE void BBX87Write(float80_t* p,BBX87Bits v){__builtin_memcpy(p,&v,10);}
ALWAYS_INLINE unsigned BBX87Index(State& s,RF80W p){return unsigned((reinterpret_cast<addr_t>(p.val_ref)-reinterpret_cast<addr_t>(&s.st.elems[0].val))/sizeof(s.st.elems[0]));}
ALWAYS_INLINE uint16_t BBX87Status(State& s){uint16_t v=s.x87.fxsave.swd.flat&~uint16_t(0x477f);v|=(s.sw.ie&1)|((s.sw.de&1)<<1)|((s.sw.ze&1)<<2)|((s.sw.oe&1)<<3)|((s.sw.ue&1)<<4)|((s.sw.pe&1)<<5)|((s.sw.sf&1)<<6)|((s.sw.c0&1)<<8)|((s.sw.c1&1)<<9)|((s.sw.c2&1)<<10)|((s.sw.c3&1)<<14);return v;}
ALWAYS_INLINE void BBX87SetStatus(State& s,uint16_t v){s.x87.fxsave.swd.flat=v;s.sw.ie=v&1;s.sw.de=(v>>1)&1;s.sw.ze=(v>>2)&1;s.sw.oe=(v>>3)&1;s.sw.ue=(v>>4)&1;s.sw.pe=(v>>5)&1;s.sw.sf=(v>>6)&1;s.sw.c0=(v>>8)&1;s.sw.c1=(v>>9)&1;s.sw.c2=(v>>10)&1;s.sw.c3=(v>>14)&1;}
ALWAYS_INLINE void BBX87Pending(Memory* m,State& s){unsigned pending=BBX87Status(s)&~s.x87.fxsave.cwd.flat&63;if(pending)__bb_native_x87_fault(m,&s,pending);}
ALWAYS_INLINE bool BBX87Occupied(State& s,unsigned logical){return (s.x87.fxsave.ftw.flat>>((s.x87.fxsave.swd.top+logical)&7))&1;}
ALWAYS_INLINE void BBX87Occupy(State& s,unsigned logical){s.x87.fxsave.ftw.flat|=uint8_t(1u<<((s.x87.fxsave.swd.top+logical)&7));}
ALWAYS_INLINE bool BBX87Raise(State& s,unsigned flags,bool stack=false,bool overflow=false){auto sw=BBX87Status(s);sw|=flags;if(stack){sw|=0x40;sw=(sw&~0x200)|(overflow?0x200:0);}unsigned unmasked=flags&~s.x87.fxsave.cwd.flat&63;if(unmasked)sw|=0x8080;BBX87SetStatus(s,sw);return unmasked!=0;}
ALWAYS_INLINE void BBX87Pop(State& s){auto v=BBX87Read(&s.st.elems[0].val);s.x87.fxsave.ftw.flat&=uint8_t(~(1u<<s.x87.fxsave.swd.top));for(unsigned i=0;i<7;++i)BBX87Write(&s.st.elems[i].val,BBX87Read(&s.st.elems[i+1].val));BBX87Write(&s.st.elems[7].val,v);BBX87SetStatus(s,uint16_t((BBX87Status(s)&~0x3800)|(((s.x87.fxsave.swd.top+1)&7)<<11)));}
ALWAYS_INLINE void BBX87Push(State& s,BBX87Bits v){for(unsigned i=7;i>0;--i)BBX87Write(&s.st.elems[i].val,BBX87Read(&s.st.elems[i-1].val));BBX87Write(&s.st.elems[0].val,v);BBX87SetStatus(s,uint16_t((BBX87Status(s)&~0x3800)|(((s.x87.fxsave.swd.top+7)&7)<<11)));BBX87Occupy(s,0);}
ALWAYS_INLINE BBX87Bits BBX87Indefinite(){return {0xc000000000000000ULL,0xffff};}
// Policy bits 4/5 explicitly preserve comparison C1 and OF/SF/AF. Neither
// host observations nor documentation differences implicitly select a guest.
ALWAYS_INLINE void BBX87Instruction(Memory* m,State& s,addr_t pc,uint16_t fop,bool mem,addr_t address,bool unmasked=false,bool comparison=false){auto profile=__bb_native_x87_image_policy(m,&s);if(comparison){if(!(profile&16))BBX87SetStatus(s,BBX87Status(s)&~uint16_t(0x200));if(!(profile&32))s.aflag.of=s.aflag.sf=s.aflag.af=0;}s.x87.fxsave.ip=pc;if(!(profile&8)||unmasked)s.x87.fxsave.fop=fop;bool update=mem&&(!(profile&4)||unmasked);if(update)s.x87.fxsave.dp=address;__bb_native_x87_record_instruction(m,&s,pc,uint32_t(mem)|(uint32_t(update)<<1),address);}

template<bool One> DEF_SEM(BBX87Constant,PC pc,I16 fop){BBX87Pending(memory,state);bool full=BBX87Occupied(state,7);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));BBX87Bits v=One?BBX87Bits{0x8000000000000000ULL,0x3fff}:BBX87Bits{0,0};bool blocked=full&&BBX87Raise(state,1,true,true);BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;if(full)v=BBX87Indefinite();BBX87Push(state,v);return memory;}
DEF_SEM(BBX87Initialize){unsigned top=state.x87.fxsave.swd.top;BBX87Bits values[8];for(unsigned i=0;i<8;++i)values[i]=BBX87Read(&state.st.elems[i].val);for(unsigned i=0;i<8;++i)BBX87Write(&state.st.elems[i].val,values[(i+8-top)&7]);state.x87.fxsave.cwd.flat=0x37f;BBX87SetStatus(state,0);state.x87.fxsave.ftw.flat=0;state.x87.fxsave.ip=0;state.x87.fxsave.dp=0;state.x87.fxsave.fop=0;__bb_native_x87_set_pointer_segments(memory,&state,0);return memory;}
DEF_SEM(BBX87LoadControl,M16 src){BBX87Pending(memory,state);state.x87.fxsave.cwd.flat=uint16_t((Read(src)&0x1f3f)|0x40);auto sw=BBX87Status(state)&~uint16_t(0x8080);if(sw&~state.x87.fxsave.cwd.flat&63)sw|=0x8080;BBX87SetStatus(state,sw);return memory;}
DEF_SEM(BBX87StoreControl,M16W dst){Write(dst,state.x87.fxsave.cwd.flat);return memory;}
template<typename D> DEF_SEM(BBX87StoreStatus,D dst){auto sw=BBX87Status(state);BBX87SetStatus(state,sw);Write(dst,sw);return memory;}
DEF_SEM(BBX87Wait){BBX87Pending(memory,state);return memory;}
DEF_SEM(BBX87Exchange,RF80W dst1,RF80W src1,RF80W dst2,RF80W src2,PC pc,I16 fop){BBX87Pending(memory,state);unsigned a=BBX87Index(state,src1),b=BBX87Index(state,src2);bool empty_a=!BBX87Occupied(state,a),empty_b=!BBX87Occupied(state,b);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool blocked=(empty_a||empty_b)&&BBX87Raise(state,1,true);BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;auto first=empty_a?BBX87Indefinite():BBX87Read(src1.val_ref);auto second=empty_b?BBX87Indefinite():BBX87Read(src2.val_ref);BBX87Write(dst1.val_ref,second);BBX87Write(dst2.val_ref,first);BBX87Occupy(state,BBX87Index(state,dst1));BBX87Occupy(state,BBX87Index(state,dst2));return memory;}
DEF_SEM(BBX87StorePop,RF80W dst,RF80W src,PC pc,I16 fop){BBX87Pending(memory,state);bool empty=!BBX87Occupied(state,BBX87Index(state,src));BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool blocked=empty&&BBX87Raise(state,1,true);BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;BBX87Write(dst.val_ref,empty?BBX87Indefinite():BBX87Read(src.val_ref));BBX87Occupy(state,BBX87Index(state,dst));BBX87Pop(state);return memory;}

template<bool Pop> DEF_SEM(BBX87UnorderedCompare,RF80W src1,RF80W src2,PC pc,I16 fop){
 BBX87Pending(memory,state);
 auto a=BBX87Read(src1.val_ref),b=BBX87Read(src2.val_ref);unsigned ea=a.sign_exponent&0x7fff,eb=b.sign_exponent&0x7fff;bool ja=(a.significand>>63)!=0,jb=(b.significand>>63)!=0;
 bool empty=!BBX87Occupied(state,BBX87Index(state,src1))||!BBX87Occupied(state,BBX87Index(state,src2));bool unsupported=(ea&&!ja)||(eb&&!jb);bool nan_a=ea==0x7fff&&a.significand!=0x8000000000000000ULL,nan_b=eb==0x7fff&&b.significand!=0x8000000000000000ULL;bool invalid=empty||unsupported||(nan_a&&!(a.significand&(1ULL<<62)))||(nan_b&&!(b.significand&(1ULL<<62)));
 // Intel PII specification update A16 and two independent host probes support flag writes even for newly raised unmasked invalid. AMD Jaguar equivalence remains open.
 bool invalid_unmasked=invalid&&BBX87Raise(state,1,empty);
 bool unordered=empty||unsupported||nan_a||nan_b,less=false,equal=false;
 bool denormal_unmasked=!unordered&&((!ea&&a.significand)||(!eb&&b.significand))&&BBX87Raise(state,2);
 if(!unordered){if(!ea&&ja)ea=1;if(!eb&&jb)eb=1;bool za=!ea&&!a.significand,zb=!eb&&!b.significand;bool sa=a.sign_exponent>>15,sb=b.sign_exponent>>15;equal=(za&&zb)||(sa==sb&&ea==eb&&a.significand==b.significand);bool magnitude_less=ea<eb||(ea==eb&&a.significand<b.significand);less=!equal&&(sa!=sb?sa:(sa?!magnitude_less:magnitude_less));}
 FLAG_CF=unordered||less;FLAG_PF=unordered;FLAG_ZF=unordered||equal;BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,invalid_unmasked||denormal_unmasked,true);if(Pop&&!invalid_unmasked&&!denormal_unmasked)BBX87Pop(state);return memory;
}
}
DEF_ISEL(FLD1)=BBX87Constant<true>;
DEF_ISEL(FLDZ)=BBX87Constant<false>;
DEF_ISEL(FNINIT)=BBX87Initialize;
DEF_ISEL(FLDCW_MEMmem16)=BBX87LoadControl;
DEF_ISEL(FNSTCW_MEMmem16)=BBX87StoreControl;
DEF_ISEL(FNSTSW_MEMmem16)=BBX87StoreStatus<M16W>;
DEF_ISEL(FNSTSW_AX)=BBX87StoreStatus<R16W>;
DEF_ISEL(FWAIT)=BBX87Wait;
DEF_ISEL(FXCH_ST0_X87)=BBX87Exchange;
DEF_ISEL(FXCH_ST0_X87_DFC1)=BBX87Exchange;
DEF_ISEL(FXCH_ST0_X87_DDC1)=BBX87Exchange;
DEF_ISEL(FSTP_X87_ST0)=BBX87StorePop;
DEF_ISEL(FSTP_X87_ST0_DFD0)=BBX87StorePop;
DEF_ISEL(FSTP_X87_ST0_DFD1)=BBX87StorePop;
DEF_ISEL(FUCOMI_ST0_X87)=BBX87UnorderedCompare<false>;
DEF_ISEL(FUCOMIP_ST0_X87)=BBX87UnorderedCompare<true>;
