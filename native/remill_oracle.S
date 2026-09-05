# SPDX-License-Identifier: GPL-2.0-or-later
# Single-threaded full GPR/YMM oracle bridge for isolated user-mode x64 fixtures.
.text
.globl oracle_enter
oracle_enter:
  pushq %rbp
  pushq %rbx
  pushq %rsi
  pushq %rdi
  pushq %r12
  pushq %r13
  pushq %r14
  pushq %r15
  subq $280, %rsp
  vmovdqu %xmm0, 0(%rsp)
  vmovdqu %xmm1, 16(%rsp)
  vmovdqu %xmm2, 32(%rsp)
  vmovdqu %xmm3, 48(%rsp)
  vmovdqu %xmm4, 64(%rsp)
  vmovdqu %xmm5, 80(%rsp)
  vmovdqu %xmm6, 96(%rsp)
  vmovdqu %xmm7, 112(%rsp)
  vmovdqu %xmm8, 128(%rsp)
  vmovdqu %xmm9, 144(%rsp)
  vmovdqu %xmm10, 160(%rsp)
  vmovdqu %xmm11, 176(%rsp)
  vmovdqu %xmm12, 192(%rsp)
  vmovdqu %xmm13, 208(%rsp)
  vmovdqu %xmm14, 224(%rsp)
  vmovdqu %xmm15, 240(%rsp)
  stmxcsr 256(%rsp)
  movq %rsp, bridge_host_rsp(%rip)
  movq %rcx, bridge_frame(%rip)
  movq %rdx, bridge_entry(%rip)
  movq %rcx, %r11
  vmovdqu 160(%r11), %ymm0
  vmovdqu 192(%r11), %ymm1
  vmovdqu 224(%r11), %ymm2
  vmovdqu 256(%r11), %ymm3
  vmovdqu 288(%r11), %ymm4
  vmovdqu 320(%r11), %ymm5
  vmovdqu 352(%r11), %ymm6
  vmovdqu 384(%r11), %ymm7
  vmovdqu 416(%r11), %ymm8
  vmovdqu 448(%r11), %ymm9
  vmovdqu 480(%r11), %ymm10
  vmovdqu 512(%r11), %ymm11
  vmovdqu 544(%r11), %ymm12
  vmovdqu 576(%r11), %ymm13
  vmovdqu 608(%r11), %ymm14
  vmovdqu 640(%r11), %ymm15
  ldmxcsr 136(%r11)
  pushq 128(%r11)
  popfq
  movq 0(%r11), %rax
  movq 8(%r11), %rbx
  movq 16(%r11), %rcx
  movq 24(%r11), %rdx
  movq 32(%r11), %rsi
  movq 40(%r11), %rdi
  movq 48(%r11), %rbp
  movq 56(%r11), %rsp
  movq 64(%r11), %r8
  movq 72(%r11), %r9
  movq 80(%r11), %r10
  movq 96(%r11), %r12
  movq 104(%r11), %r13
  movq 112(%r11), %r14
  movq 120(%r11), %r15
  movq 88(%r11), %r11
  jmpq *bridge_entry(%rip)
.globl oracle_return
oracle_return:
  movq %rax, bridge_rax(%rip)
  movq %r11, bridge_r11(%rip)
  movq bridge_frame(%rip), %rax
  movq %rbx, 8(%rax)
  movq %rcx, 16(%rax)
  movq %rdx, 24(%rax)
  movq %rsi, 32(%rax)
  movq %rdi, 40(%rax)
  movq %rbp, 48(%rax)
  movq %rsp, 56(%rax)
  movq %r8, 64(%rax)
  movq %r9, 72(%rax)
  movq %r10, 80(%rax)
  movq %r12, 96(%rax)
  movq %r13, 104(%rax)
  movq %r14, 112(%rax)
  movq %r15, 120(%rax)
  movq bridge_host_rsp(%rip), %rsp
  pushfq
  popq 128(%rax)
  stmxcsr 136(%rax)
  vmovdqu %ymm0, 160(%rax)
  vmovdqu %ymm1, 192(%rax)
  vmovdqu %ymm2, 224(%rax)
  vmovdqu %ymm3, 256(%rax)
  vmovdqu %ymm4, 288(%rax)
  vmovdqu %ymm5, 320(%rax)
  vmovdqu %ymm6, 352(%rax)
  vmovdqu %ymm7, 384(%rax)
  vmovdqu %ymm8, 416(%rax)
  vmovdqu %ymm9, 448(%rax)
  vmovdqu %ymm10, 480(%rax)
  vmovdqu %ymm11, 512(%rax)
  vmovdqu %ymm12, 544(%rax)
  vmovdqu %ymm13, 576(%rax)
  vmovdqu %ymm14, 608(%rax)
  vmovdqu %ymm15, 640(%rax)
  movq bridge_r11(%rip), %rcx
  movq %rcx, 88(%rax)
  movq bridge_rax(%rip), %rcx
  movq %rcx, 0(%rax)
  ldmxcsr 256(%rsp)
  vmovdqu 0(%rsp), %xmm0
  vmovdqu 16(%rsp), %xmm1
  vmovdqu 32(%rsp), %xmm2
  vmovdqu 48(%rsp), %xmm3
  vmovdqu 64(%rsp), %xmm4
  vmovdqu 80(%rsp), %xmm5
  vmovdqu 96(%rsp), %xmm6
  vmovdqu 112(%rsp), %xmm7
  vmovdqu 128(%rsp), %xmm8
  vmovdqu 144(%rsp), %xmm9
  vmovdqu 160(%rsp), %xmm10
  vmovdqu 176(%rsp), %xmm11
  vmovdqu 192(%rsp), %xmm12
  vmovdqu 208(%rsp), %xmm13
  vmovdqu 224(%rsp), %xmm14
  vmovdqu 240(%rsp), %xmm15
  addq $280, %rsp
  popq %r15
  popq %r14
  popq %r13
  popq %r12
  popq %rdi
  popq %rsi
  popq %rbx
  popq %rbp
  retq
.data
.p2align 3
bridge_host_rsp: .quad 0
bridge_frame: .quad 0
bridge_entry: .quad 0
bridge_rax: .quad 0
bridge_r11: .quad 0
