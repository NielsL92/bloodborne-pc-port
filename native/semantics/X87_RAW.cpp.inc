// SPDX-License-Identifier: Apache-2.0
// Raw extended transfers never enter floating arithmetic. Metadata is a runtime
// contract keyed by the exact decoded guest PC, including segment selection.
// Image policy bits 2/3 select FDP/FOP updates only on a new unmasked exception.
// Record flags: bit 0 is a memory operand, bit 1 means its FDP was updated.
// BB_REPLACE_SELECTOR: FLD_ST0_MEMmem80real
// BB_REPLACE_SELECTOR: FSTP_MEMmem80real_ST0
// BB_REPLACE_SELECTOR: FLD_ST0_X87
// BB_REPLACE_SELECTOR: FCHS
// BB_REPLACE_SELECTOR: FCMOVNE_ST0_X87
extern "C" void __bb_native_x87_record_instruction(Memory*,State*,addr_t,uint32_t,addr_t);
namespace {
ALWAYS_INLINE void BBX87RawInstruction(Memory* m,State& s,addr_t pc,uint16_t fop,bool mem,addr_t address,bool unmasked=false){auto profile=__bb_native_x87_image_policy(m,&s);s.x87.fxsave.ip=pc;if(!(profile&8)||unmasked)s.x87.fxsave.fop=fop;bool update=mem&&(!(profile&4)||unmasked);if(update)s.x87.fxsave.dp=address;__bb_native_x87_record_instruction(m,&s,pc,uint32_t(mem)|(uint32_t(update)<<1),address);}

DEF_SEM(BBX87LoadRaw80,RF80W,M8 src,PC pc,I16 fop){
 BBX87Pending(memory,state);auto address=AddressOf(src);__bb_native_x87_check_span(memory,&state,address,10,0,1);uint8_t bytes[10];for(unsigned i=0;i<10;++i)bytes[i]=__remill_read_memory_8(memory,address+i);BBX87Bits value;__builtin_memcpy(&value,bytes,10);
 BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool full=BBX87Occupied(state,7);bool blocked=full&&BBX87Raise(state,1,true,true);BBX87RawInstruction(memory,state,Read(pc),Read(fop),true,address,blocked);if(blocked)return memory;if(full)value=BBX87Indefinite();BBX87Push(state,value);return memory;
}
DEF_SEM(BBX87StoreRaw80,M8W dst,RF80W src,PC pc,I16 fop){
 BBX87Pending(memory,state);auto address=AddressOf(dst);__bb_native_x87_check_span(memory,&state,address,10,1,1);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool empty=!BBX87Occupied(state,BBX87Index(state,src));bool blocked=empty&&BBX87Raise(state,1,true);BBX87RawInstruction(memory,state,Read(pc),Read(fop),true,address,blocked);if(blocked)return memory;
 auto value=empty?BBX87Indefinite():BBX87Read(src.val_ref);uint8_t bytes[10];__builtin_memcpy(bytes,&value,10);for(unsigned i=0;i<10;++i)memory=__remill_write_memory_8(memory,address+i,bytes[i]);BBX87Pop(state);return memory;
}
DEF_SEM(BBX87LoadRegister,RF80W,RF80W src,PC pc,I16 fop){
 BBX87Pending(memory,state);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool full=BBX87Occupied(state,7),empty=!BBX87Occupied(state,BBX87Index(state,src));auto value=BBX87Read(src.val_ref);bool blocked=(full||empty)&&BBX87Raise(state,1,true,full&&!empty);BBX87RawInstruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;if(full||empty)value=BBX87Indefinite();BBX87Push(state,value);return memory;
}
DEF_SEM(BBX87ChangeSign,PC pc,I16 fop){
 BBX87Pending(memory,state);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool empty=!BBX87Occupied(state,0);bool blocked=empty&&BBX87Raise(state,1,true);BBX87RawInstruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;auto value=empty?BBX87Indefinite():BBX87Read(&state.st.elems[0].val);if(!empty)value.sign_exponent^=0x8000;BBX87Write(&state.st.elems[0].val,value);BBX87Occupy(state,0);return memory;
}
DEF_SEM(BBX87MoveNotEqual,RF80W dst,RF80W src,PC pc,I16 fop){
 BBX87Pending(memory,state);bool empty=!BBX87Occupied(state,BBX87Index(state,dst))||!BBX87Occupied(state,BBX87Index(state,src));bool blocked=empty&&BBX87Raise(state,1,true);BBX87RawInstruction(memory,state,Read(pc),Read(fop),false,0,blocked);if(blocked)return memory;
 if(empty||!state.aflag.zf){BBX87Write(dst.val_ref,empty?BBX87Indefinite():BBX87Read(src.val_ref));BBX87Occupy(state,BBX87Index(state,dst));}return memory;
}
}
DEF_ISEL(FLD_ST0_MEMmem80real)=BBX87LoadRaw80;
DEF_ISEL(FSTP_MEMmem80real_ST0)=BBX87StoreRaw80;
DEF_ISEL(FLD_ST0_X87)=BBX87LoadRegister;
DEF_ISEL(FCHS)=BBX87ChangeSign;
DEF_ISEL(FCMOVNE_ST0_X87)=BBX87MoveNotEqual;
