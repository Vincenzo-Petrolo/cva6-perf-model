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
        addi sp, sp, -4

        addi t0, t1, 10
        sw t0, 0(sp)
        lw t1, 0(sp)
        add t2, t0, t1

        addi sp, sp, 4
        
        j tohost_exit # just terminate with exit code 0

# a0 exit code
tohost_exit:
        slli a0, a0, 1
        ori a0, a0, 1

        la t0, tohost
        sw a0, 0(t0)

        1: j 1b # wait for termination