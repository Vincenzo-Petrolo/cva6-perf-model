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
        lw t0, 0(sp)
        lw t1, 4(sp)
        lw t2, 8(sp)
        lw t3, 12(sp)
        addi sp, sp, 16
        
        j tohost_exit # just terminate with exit code 0

# a0 exit code
tohost_exit:
        slli a0, a0, 1
        ori a0, a0, 1

        la t0, tohost
        sw a0, 0(t0)

        1: j 1b # wait for termination