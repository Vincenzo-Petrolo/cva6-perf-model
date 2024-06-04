import subprocess
import re
import sys

RISCV_STRING = 'riscv32-unknown-elf-'

def extract_symbols(object_file):
    result = subprocess.run([RISCV_STRING+'nm', object_file], stdout=subprocess.PIPE)
    symbols = result.stdout.decode('utf-8')
    return symbols

def extract_data_section(object_file):
    result = subprocess.run([RISCV_STRING+'objdump', '-s', '-j', '.data', object_file], stdout=subprocess.PIPE)
    data_section = result.stdout.decode('utf-8')
    return data_section

def parse_symbols(symbols):
    symbol_table = {}
    for line in symbols.split('\n'):
        match = re.match(r'([0-9a-fA-F]+) \w (.+)', line)
        if match:
            address, name = match.groups()
            symbol_table[name] = int(address, 16)
    return symbol_table

def parse_data_section(data_section):
    data = {}
    lines = data_section.split('\n')
    address = None
    for line in lines:
        match = re.match(r'\s*([0-9a-fA-F]+)\s+(.+)', line)
        if match:
            address, values = match.groups()
            address = int(address, 16)
            values = bytes.fromhex(values.replace(' ', ''))
            data[address] = values
    return data

# Extract symbols and data section
symbols = extract_symbols(sys.argv[1])
data_section = extract_data_section(sys.argv[1])

# Parse the symbols and data section
symbol_table = parse_symbols(symbols)
data = parse_data_section(data_section)

# Display the extracted data
print("Symbols:", symbol_table)
print("Data Section:", data)

# Initialize virtual memory in Python
virtual_memory = bytearray(1024)  # Example size

for address, values in data.items():
    virtual_memory[address:address+len(values)] = values

# Now you can access your initialized variables
tohost_address = symbol_table['tohost']
fromhost_address = symbol_table['fromhost']

tohost_value = int.from_bytes(virtual_memory[tohost_address:tohost_address+8], 'little')
fromhost_value = int.from_bytes(virtual_memory[fromhost_address:fromhost_address+8], 'little')

print("tohost:", tohost_value)
print("fromhost:", fromhost_value)
