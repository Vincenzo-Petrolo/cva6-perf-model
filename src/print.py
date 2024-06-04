
def convertToHex(value):
    if (value is not None and isinstance(value, int)):
        return hex(int(value))