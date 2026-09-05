# Authored callback; negative input requests an explicit nonlocal escape.
.intel_syntax noprefix
.text
.globl fixture
fixture:
 push rbx
 mov rbx, rdx
 test rdi, rdi
 js escape
 lea rax, [rdi + rdi*2]
 pop rbx
 ret
escape:
 call rsi
 mov qword ptr [rbx], 99
 pop rbx
 ret
