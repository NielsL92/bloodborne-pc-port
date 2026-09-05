.intel_syntax noprefix
.text
.globl fixture
fixture:
 mov qword ptr [rdi],rsi
 mfence
 mov qword ptr [rdi+8],1
 ret
