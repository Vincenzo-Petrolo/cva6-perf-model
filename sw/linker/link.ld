MEMORY
{
  RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 0x100000
}

SECTIONS
{
  .text : { *(.text*) } > RAM
  .data : { *(.data*) } > RAM
  .bss : { *(.bss*) } > RAM
  .heap : { *(.heap*) } > RAM
  .stack : { *(.stack*) } > RAM
}