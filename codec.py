from config import SYNC_PATTERN, REPETITION

def encode(data):
    binary = ''.join(format(ord(c), '08b') for c in data)
    binary = ''.join(bit * REPETITION for bit in binary)
    return SYNC_PATTERN + binary

def majority(bits):
    return '1' if bits.count('1') > bits.count('0') else '0'

def decode(bitstream):
    start = bitstream.find(SYNC_PATTERN)
    if start == -1:
        return ""

    data = bitstream[start + len(SYNC_PATTERN):]

    decoded = []
    for i in range(0, len(data), REPETITION):
        group = data[i:i+REPETITION]
        if len(group) == REPETITION:
            decoded.append(majority(group))

    binary = ''.join(decoded)

    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))

    return ''.join(chars)