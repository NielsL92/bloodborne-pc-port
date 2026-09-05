.intel_syntax noprefix
.text
.globl fixture
fixture:
again:
 mov rax,qword ptr [rdi+8]
 test rax,rax
 jz again
 mfence
 mov rax,qword ptr [rdi]
 mfence
 mov qword ptr [rdi+8],0
 ret
