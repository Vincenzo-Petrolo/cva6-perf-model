# to communicate with the host
# check riscv-software-src/riscv-tests
.section .tohost, "aw", @progbits

.align 6
.globl tohost
tohost: .dword 0

.align 6
.globl fromhost
fromhost: .dword 0

.section .text

.globl _start

_start:
        addi sp, sp, -16
        add t0, t1, t2
        beq t0, t1, B
        addi t0, t0, 1
        addi t0, t0, 2
        addi t0, t0, 3
B:
        j tohost_exit # just terminate with exit code 0

# a0 exit code
tohost_exit:
        slli a0, a0, 1
        ori a0, a0, 1

        la t0, tohost
        sw a0, 0(t0)

        1: j 1b # wait for termination