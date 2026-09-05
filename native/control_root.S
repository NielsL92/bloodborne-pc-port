# Authored ABI/control-flow fixture, not game code.
.intel_syntax noprefix
.text
.globl fixture
fixture:
 push rbx
 mov rbx, rcx
 call rdx
 mov [rbx], rax
 add rax, 7
 pop rbx
 ret
