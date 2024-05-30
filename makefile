#############################
# ----- CONFIGURATION ----- #
#############################

# General configuration
MAKE			?= make
BUILD_DIR		?= build

# Target application
PROJECT			?= add
SW_DIR			?= sw
LINKER 			?= $(SW_DIR)/linker/link.ld
SRCS 			:= $(wildcard $(SW_DIR)/applications/$(PROJECT)/*.c)
SRCS 			+= $(wildcard $(SW_DIR)/applications/$(PROJECT)/*.S)
OBJS 			:= $(filter %.o,\
				   $(patsubst %.c,$(BUILD_DIR)/%.o,$(SRCS))\
				   $(patsubst %.S,$(BUILD_DIR)/%.o,$(SRCS)))
INC_DIRS 		:= $(sort $(dir $(SRCS)))
INC_DIRS_GCC	:= $(addprefix -I ,$(INCLUDE_DIRS))

###  RISC-V C toolchain
# TODO: REMOVE -mstrict-align ONCE UNALIGNED ACCESS IS SUPPORTED
RISCV_EXE_PREFIX           	?= riscv32-unknown-elf
GCC_VERSION					:= $(shell $(RISCV_EXE_PREFIX)-gcc -dumpversion)
ISA_STRING				?= rv32i
ABI_STRING					?= ilp32
COPT						?= -O0
CDEFS						?= # SPIKE_CHECK if using Spike
CFLAGS			:= -march=$(ISA_STRING) \
				   -mabi=$(ABI_STRING) \
				   -mstrict-align \
				   -nostartfiles \
				   -flto \
				   -ffunction-sections \
				   -fdata-sections \
				   -fno-builtin \
				   $(COPT) \
				   -Wall
LDFLAGS_PRE		:= -T $(LINKER) \

# Export all the variables to sub-makefiles
export

#######################
# ----- TARGETS ----- #
#######################

# Software build
# --------------
# Application build
.PHONY: app
app: $(BUILD_DIR)/main.hex $(BUILD_DIR)/main.disasm $(BUILD_DIR)/main.elf

$(BUILD_DIR)/main.%: $(BUILD_DIR)/applications/$(PROJECT)/main.%
	cp $< $@

# ASCII .hex firmware
$(BUILD_DIR)/%.hex: $(BUILD_DIR)/main.elf
	$(RISCV_EXE_PREFIX)-objcopy -O verilog $< $@

# Disassembly
$(BUILD_DIR)/%.disasm: $(BUILD_DIR)/%.elf
	$(RISCV_EXE_PREFIX)-objdump -D $< > $@

# Stripped binary firmware
$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
	$(RISCV_EXE_PREFIX)-objcopy -O binary $< $@

# Linked executable firmware
$(BUILD_DIR)/%.elf: $(OBJS)
	$(RISCV_EXE_PREFIX)-gcc $(CFLAGS) $(LDFLAGS_PRE) $(INC_FOLDERS_GCC) $^ $(LDFLAGS_POST) -o $@

# Implicit compilation rules
$(BUILD_DIR)/%.o: ./%.c | $(BUILD_DIR)/applications/$(PROJECT)/
	@mkdir -p $(@D)
	$(RISCV_EXE_PREFIX)-gcc $(CFLAGS) $(CDEFS) $(LDFLAGS_PRE) $(INC_FOLDERS_GCC) -c $< -o $@
$(BUILD_DIR)/%.o: ./%.S | $(BUILD_DIR)/applications/$(PROJECT)/
	@mkdir -p $(@D)
	$(RISCV_EXE_PREFIX)-gcc $(CFLAGS) $(CDEFS) $(INC_FOLDERS_GCC) -c $< -o $@

.PHONY: spike-trace
spike-trace: $(BUILD_DIR)/spike-trace.log
$(BUILD_DIR)/spike-trace.log: $(BUILD_DIR)/main.elf
	@echo "## Running simulation with Spike..."
	spike --log=$@ -l --isa=rv32i $<
	cp $@ $(BUILD_DIR)/applications/$(PROJECT)/


# Utils
# -----
# Create new directories
%/:
	mkdir -p $@

# Print variables
.PHONY: .print
.print:
	@echo "RISCV:        $(RISCV)"
	@echo "PROJECT:      $(PROJECT)"
	@echo "SRCS          $(SRCS)"
	@echo "OBJS          $(OBJS)"
	@echo "LIB_SRCS:     $(LIB_SRCS)"
	@echo "LIB_OBJS:     $(LIB_OBJS)"
	@echo "LIB_INCS:     $(LIB_INCS)"
	@echo "INC_FOLDERS:  $(INC_FOLDERS)"
	@echo "CFLAGS:       $(CFLAGS)"
	@echo "LDFLAGS_PRE:  $(LDFLAGS_PRE)"
	@echo "LDFLAGS_POST: $(LDFLAGS_POST)"

# Clean-up
.PHONY: clean
clean:
	$(RM) -r $(BUILD_DIR)
