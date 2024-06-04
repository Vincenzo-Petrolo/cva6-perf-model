MEMORY
{
  RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 0x100000
}

SECTIONS
{
  __stack_size = DEFINED(__stack_size) ? __stack_size : 64K;
  PROVIDE(__stack_size = __stack_size);

  .text : { *(.text*) } > RAM
  .data : { *(.data*) } > RAM
  .bss : { *(.bss*) } > RAM
  .heap : { *(.heap*) } > RAM
  .stack  :
  {
    PROVIDE (__stack_bottom = .);
    . = __stack_size;
    PROVIDE (_sp = .);
    PROVIDE (__stack_top = .);
  } > RAM

}