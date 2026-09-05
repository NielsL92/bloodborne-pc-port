.intel_syntax noprefix
.text
.globl fixture
fixture:
 mov rax,rsi
 lock xadd qword ptr [rdi],rax
 ret
