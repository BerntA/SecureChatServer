#
# Misc utility functions
#

def circular_left_shift(n, shift, num_bits = 8):
    """
    Perform a left circular shift.
    """
    return (((n << shift)) | (n >> (num_bits - shift)))

def get_as_bits(txt):
    return "".join([format(ord(v), '08b') for v in list(txt)])

def get_as_text(bits):
    return "".join([chr(int(bits[i:(i+8)],2)) for i in range(0, len(bits), 8)])
    