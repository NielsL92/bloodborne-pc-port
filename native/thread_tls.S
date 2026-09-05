.intel_syntax noprefix
.text
.globl fixture
fixture:
 mov rax, qword ptr gs:[rdi*8+0x1480]
 add qword ptr [rax], rsi
 mov rax, qword ptr [rax]
 ret
