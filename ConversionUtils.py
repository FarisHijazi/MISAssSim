import re
import struct
import ctypes

# FIXME:    changing from to a floating point is actually parsing the value, we don't want this
#           it should represent the same value differently
#           Basically it's parsing it and not getting the same value

escapedChars = {
    # Escape Sequence Character Definition ASCII Value
    r'\0': 0,  # Null Character
    r'\b': 8,  # Backspace
    r'\t': 9,  # Tab
    r'\n': 10,  # Newline
    r'\f': 12,  # Form feed
    r'\r': 13,  # Carriage return
    r'\'': 39,  # Single Quote
    r'\"': 34,  # Double Quote
    r'\\': 9,  # Backslash
}


def parseDoubleStr(string):
    return 0 if not string else ctypes.c_uint.from_buffer(ctypes.c_double(float(string))).value

def parseFloatStr(string):
    return 0 if not string else ctypes.c_uint.from_buffer(ctypes.c_float(float(string))).value

def parseDecStr(string):
    return 0 if not string else int(string)


def parseHexStr(string):
    return 0 if not string else int(string, 16)


def parseBinStr(string):
    return 0 if not string else int(string, 2)


def parseAsciiStr(string):
    # if is escaped char, the fallback to direct conversion
    return 0 if not string else escapedChars.get(string) if string in escapedChars else ord(string[0])


representationParsers = {
    'bin': parseBinStr,
    'dec': parseDecStr,
    'hex': parseHexStr,
    'ascii': parseAsciiStr,
    'sp': parseFloatStr,
    'dp': parseDoubleStr,
}
addressBits = 64
addressBytes = addressBits // 8
entrySize = 8  # in bytes


def val2ascii(val):
    try:
        return chr(val)
    except Exception as e:
        return None

# 0x3f800000 -> float32: 1.0000
# dec: 1 -> float32: 1.401298....-45
def float2str(val, sourceSize=addressBytes):
    sourceSize = max(sourceSize, len(bytearray(val)))
    buf = (ctypes.c_char * sourceSize)() # should be 8 bytes (64bits)
    cval = ctypes.c_ulong(val)

    ctypes.memmove(buf, ctypes.byref(cval), ctypes.sizeof(cval))

    # ctypes.memmove(buf, ctypes.byref(val), ctypes.sizeof(val))
    return re.sub(r'\s', '', format(ctypes.c_float.from_buffer(buf).value, str(addressBits)+'f'))

def double2str(val, sourceSize=addressBytes):
    sourceSize = max(sourceSize, len(bytearray(val)))
    buf = (ctypes.c_char * sourceSize)() # should be 8 bytes (64bits)
    cval = ctypes.c_ulong(val)

    ctypes.memmove(buf, ctypes.byref(cval), ctypes.sizeof(cval))

    # ctypes.memmove(buf, ctypes.byref(val), ctypes.sizeof(val))
    return re.sub(r'\s', '', format(ctypes.c_double.from_buffer(buf).value, str(addressBits)+'f'))


# NOTE that all these assume the input value is 64bits
representationFormatter = {
    'sp': float2str,
    'dp': double2str,
    'hex': lambda val: re.sub(r'\s', '0', format(val, str(addressBytes//2)+'x')),
    'bin': lambda val: re.sub(r'\s', '0', format(val, str(addressBytes)+'b')),
    'dec': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'d')),
    'ascii': val2ascii,
}


def tobinary(num: int, src: str, dest: str):
    dest_dict = {
        'b': bin,
        'd': str,
        'l': hex,
        'a': chr,
    }
    return [dest_dict.get(src, bin)(re.sub(r'0[xbo]', '', ''.join(ord(c)))).rjust(8, '0') for c in struct.pack('!{0}'.format(src), num)]


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



def long_to_bytes(val, endianness='big'):
    from binascii import unhexlify
    """
    Use :ref:`string formatting` and :func:`~binascii.unhexlify` to
    convert ``val``, a :func:`long`, to a byte :func:`str`.

    :param long val: The value to pack

    :param str endianness: The endianness of the result. ``'big'`` for
      big-endian, ``'little'`` for little-endian.

    If you want byte- and word-ordering to differ, you're on your own.

    Using :ref:`string formatting` lets us use Python's C innards.
    """

    # one (1) hex digit per four (4) bits
    width = val.bit_length()

    # unhexlify wants an even multiple of eight (8) bits, but we don't
    # want more digits than we need (hence the ternary-ish 'or')
    width += 8 - ((width % 8) or 8)

    # format width specifier: four (4) bits per hex digit
    fmt = '%%0%dx' % (width // 4)

    # prepend zero (0) to the width, to zero-pad the output
    s = unhexlify(fmt % val)

    if endianness == 'little':
        # see http://stackoverflow.com/a/931095/309233
        s = s[::-1]

    return s

