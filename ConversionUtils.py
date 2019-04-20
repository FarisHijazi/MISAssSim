import re
import struct
import ctypes

def parseFloatStr(string):
    return 0 if not string else ctypes.c_uint.from_buffer(ctypes.c_float(float(string))).value

def parseDecStr(string):
    return 0 if not string else int(string)

def parseHexStr(string):
    return 0 if not string else int(string, 16)

def parseBinStr(string):
    return 0 if not string else int(string, 2)

def parseAsciiStr(string):
    return 0 if not string else ord(string)

representationParsers = {
    'bin': parseBinStr,
    'dec': parseDecStr,
    'hex': parseHexStr,
    'ascii': parseAsciiStr,
    'fp': parseFloatStr,
}
addressBits = 64
addressBytes = addressBits // 8
entrySize = 8  # in bytes

# representationFormatter = {
#     # TODO: replace those '' with '0's, and make the entries in the gui wider
#     'bin': lambda val: ''.join(bin(ord(str(c))).replace(r'0[bxo]', '').rjust(8, '0') for c in struct.pack('>b', val)),
#     'dec': lambda val: ''.join(str(ord(str(c))).replace(r'0[bxo]', '').rjust(8, '0') for c in struct.pack('>d', val)),
#     'hex': lambda val: ''.join(hex(ord(str(c))).replace(r'0[bxo]', '').rjust(8, '0') for c in struct.pack('>l', val)),
#     'ascii': lambda val: chr(val),
#     'fp': lambda val: ''.join(bin(ord(str(c))).replace(r'0[bxo]', '').rjust(8, '0') for c in struct.pack('>f', val)),
#     # TODO: format to floating point
# }
representationFormatter = {
    # TODO: replace those '' with '0's, and make the entries in the gui wider
    'fp': lambda val: re.sub(r'\s', '', format(val, str(addressBits)+'f')), #TODO: format to floating point
    'hex': lambda val: re.sub(r'\s', '', format(val, str(addressBytes//2)+'x')),
    'bin': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'b')),
    'dec': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'d')),
    'ascii': lambda val: (chr(val)),
}

def bekfast(val):
    return ''.join(bin(ord(c)).replace(r'0[bxo]', '').rjust(8, '0') for c in struct.pack('!f', val)),

def tobinary(num: int, src: str, dest: str):
    dest_dict = {
        'b': bin,
        'd': str,
        'l': hex,
        'a': chr,
    }
    return [dest_dict.get(src, bin)(re.sub(r'0[xbo]', '', ''.join(ord(c)))).rjust(8, '0') for c in struct.pack('!{0}'.format(src), num)]


# assuming the input value is a signed decimal value (TODO: this should become bytes)
# representationFormatter = {
#     # TODO: replace those '' with '0's, and make the entries in the gui wider
#
#     # 'fp': lambda val: str(ctypes.c_ulong.from_buffer(ctypes.c_buffer(bytes(val), ctypes.sizeof(val))).value),
#     # TODO: format to floating point
#     'hex': lambda val: hex(ctypes.c_ulong.from_buffer(ctypes.c_ulong(val)).value),
#     'bin': lambda val: bin(ctypes.c_ulong.from_buffer(ctypes.c_ulong(ctypes.sizeof(entrySize))).value),
#     'dec': lambda val: ctypes.c_ulong.from_buffer(ctypes.c_ulong(val)).value,
#     'ascii': lambda val: (chr(ctypes.c_ulong.from_buffer(ctypes.c_ulong(val)).value)),
# }

# value to string


# def frombinary(binstr:str, src):
#     return val


def tobinary(num):
    # https://stackoverflow.com/questions/16444726/binary-representation-of-float-in-python-bits-not-hex
    import struct
    # Struct can provide us with the float packed into bytes. The '!' ensures that
    # it's in network byte order (big-endian) and the 'f' says that it should be
    # packed as a float. Alternatively, for double-precision, you could use 'd'.
    packed = struct.pack('!f', num)
    print('Packed: %s' % repr(packed))

    # For each character in the returned string, we'll turn it into its corresponding
    # integer code point
    #
    # [62, 163, 215, 10] = [ord(c) for c in '>\xa3\xd7\n']
    integers = [ord(c) for c in packed]
    print('Integers: %s' % integers)

    # For each integer, we'll convert it to its binary representation.
    binaries = [bin(i) for i in integers]
    print('Binaries: %s' % binaries)

    # Now strip off the '0b' from each of these
    stripped_binaries = [s.replace('0b', '') for s in binaries]
    print('Stripped: %s' % stripped_binaries)

    # Pad each byte's binary representation's with 0's to make sure it has all 8 bits:
    #
    # ['00111110', '10100011', '11010111', '00001010']
    padded = [s.rjust(8, '0') for s in stripped_binaries]
    print('Padded: %s' % padded)

    # At this point, we have each of the bytes for the network byte ordered float
    # in an array as binary strings. Now we just concatenate them to get the total
    # representation of the float:
    return ''.join(padded)

