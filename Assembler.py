"""
Conventions to agree on:
- register arguments will be strings othwerise
"""

# from AssembledFile import AssembledFile
import re

# from tkFileDialog import *

# TODO: fix issue: the dictionaries, sometimes imm='r0' or wtver, BIG PROBLEM! test mul for an example

fileexists = False

# opcode 37 op:(func, imm_L, (imm_R|p), imm)
sec4_SHIFT_dict = {
    "shlr": (0, 'i3', 'i4', None),
    "shlr": (1, 'i3', 'i4', None),
    "salr": (2, 'i3', 'i4', None),
    "ror": (3, None, 'i3', None),
    "mul": (8, None, None, 'i3'),
    "div": (12, None, None, 'i2'),
    "mod": (13, None, None, 'i2'),
    "divu": (14, None, None, 'i2'),
    "modu": (15, None, None, 'i2'),
    # pseudo
    "shl": (0, 'i3', None, None),
    "shr": (0, None, 'i3', None),
    "sar": (2, None, 'i3', None),
    "rol": (3, None, 'i3', None),
    # extract and extend pseudo
    "extr": (2, 'i3', 'i4', None),
    "extru": (0, 'i3', 'i4', None),
    "ext": (2, 'i3', None, None),
    "extu": (0, 'i3', None, None),

    "insz": (2, 'i3', 'i4', None),
}
"""
layed out according to section/format (I'm not sure either)
"""
opcodes = {
    'j': {
        'j': 2,
        'jal': 3,
        'jr': 14,
        'ret': 14,
        'jalr': 15,
    },
    'b': {
        'beqi': 8,
        'bnei': 9,
        'blti': 10,
        'bgei': 11,
        'bltui': 12,
        'bgeui': 13,

        'beq': 16,
        'bne': 17,
        'blt': 18,
        'bge': 19,
        'bltu': 20,
        'bgeu': 21,

        # Compare with immediate (0 to 30) and Branch Pseudo Instructions :
        'ble': 10,
        'bgt': 11,
        'bleu': 13,
        'bgtu': 12,
        # -----------
        'loop': 22,
        'loopd': 23
    },

    'bzero': {
        # Compare with Zero and Branch Pseudo-Instructions (use immediate instructions) :
        'beqz': 8,
        'bnez': 9,
        'bltz': 10,
        'bgtz': 11,
        'bgez': 11,
        'blez': 10
    },

    # (opcode, func)
    'ls': {
        # All instructions below come in I-Format or R-Format
        'lb': (24, 4),
        'lh': (24, 5),
        'lw': (24, 6),
        'ld': (24, 7),

        'lbu': (24, 0),
        'lhu': (24, 1),
        'lwu': (24, 2),
        'ldu': (24, 3),

        'sb': (25, 0),
        'sh': (25, 1),
        'sw': (25, 2),
        'sd': (25, 3)
    },
    'alu': {  # ALU instructions (section 5)
        "add": 41,
        "and": 41,
        "or": 41,
        "xor": 41,
        "nadd": 41,
        "cand": 41,
        "cor": 41,
        "xnor": 41,
        "andeq": 41,
        "andne": 41,
        "andlt": 41,
        "andge": 41,
        "andltu": 41,
        "andgeu": 41,
        "oreq": 41,
        "orne": 41,
        "orlt": 41,
        "orge": 41,
        "orltu": 41,
        "orgeu": 41,
        "min": 41,
        "max": 41,
        "minu": 41,
        "maxu": 41,
        "andgt": 41,
        "andle": 41,
        "andgtu": 41,
        "andleu": 41,
        "orgt": 41,
        "orle": 41,
        "orgtu": 41,
        "orleu": 41,
        "sel": 41,
        "seln": 41,
        "selp": 41,
        "selz": 41,
        "madd": 41,
        "nmadd": 41
    },
    'fpu2': {
        "eq.s": -1,
        "eq.d": -1,
        "ne.s": -1,
        "ne.d": -1,
        "lt.s": -1,
        "lt.d": -1,
        "ge.s": -1,
        "ge.d": -1,
        "inf.s": -1,
        "inf.d": -1,
        "nan.s": -1,
        "nan.d": -1,
        "mul.s": -1,
        "mul.d": -1,
        "div.s": -1,
        "div.d": -1,
        "gt.s": -1,
        "gt.d": -1,
        "le.s": -1,
        "le.d": -1,
        "sub.s": -1,
        "sub.d": -1,
    }
}

# (p, func)
fpu1_dict = {
    "abs.s": (0, 0),
    "abs.d": (1, 0),
    "neg.s": (0, 1),
    "neg.d": (1, 1),
    "sqrt.s": (0, 2),
    "sqrt.d": (1, 2),
    "cvts.d": (0, 4),
    "cvtd.s": (1, 4),
    "cvts.i": (0, 5),
    "cvtd.i": (1, 5),
    "cvti.s": (0, 6),
    "cvti.d": (1, 6),
    "rint.s": (0, 7),
    "rint.d": (1, 7),
}

# (func, imm)
sec4_RET_dict = {
    "retadd": (0, 'i3'),
    "retnadd": (1, 'i3'),
    "retand": (2, 'i3'),
    "retcand": (3, 'i3'),
    "retor": (4, 'i3'),
    "retcor": (5, 'i3'),
    "retxor": (6, 'i3'),
    "retset": (7, 'i3'),
    "reteq": (8, 'i3'),
    "retne": (9, 'i3'),
    "retlt": (10, 'i3'),
    "retge": (11, 'i3'),
    "retltu": (12, 'i3'),
    "retgeu": (13, 'i3'),
    "retmin": (14, 'i3'),
    "retmax": (15, 'i3'),
}

# neumonic: (p, func, swap_ra_rb)
fpu2_dict = {
    "eq.s": (0, 0, False),
    "eq.d": (1, 0, False),
    "ne.s": (0, 1, False),
    "ne.d": (1, 1, False),
    "lt.s": (0, 2, False),
    "lt.d": (1, 2, False),
    "ge.s": (0, 3, False),
    "ge.d": (1, 3, False),
    "inf.s": (0, 4, False),
    "inf.d": (1, 4, False),
    "nan.s": (0, 5, False),
    "nan.d": (1, 5, False),

    "add.s": (0, 8, False),
    "add.d": (1, 8, False),
    "nadd.s": (0, 9, False),
    "nadd.d": (1, 9, False),
    "mul.s": (0, 10, False),
    "mul.d": (1, 10, False),
    "div.s": (0, 11, False),
    "div.d": (1, 11, False),
    "min.s": (0, 12, False),
    "min.d": (1, 12, False),
    "max.s": (0, 13, False),
    "max.d": (1, 13, False),

    "gt.s": (0, 2, True),
    "gt.d": (1, 2, True),
    "le.s": (0, 3, True),
    "le.d": (1, 3, True),
    "sub.s": (0, 9, True),
    "sub.d": (1, 9, True),
}
# neumonic: (p, func, swap_rc_rb)
fpu3_dict = {
    "add.s": (0, 8, False),
    "add.d": (1, 8, False),
    "nadd.s": (0, 9, False),
    "nadd.d": (1, 9, False),
    "madd.s": (0, 10, False),
    "madd.d": (1, 10, False),
    "nmadd.s": (0, 11, False),
    "nmadd.d": (1, 11, False),
    "min.s": (0, 12, False),
    "min.d": (1, 12, False),
    "max.s": (0, 13, False),
    "max.d": (1, 13, False),
    "andeq.s": (0, 0, False),
    "andeq.d": (1, 0, False),
    "andne.s": (0, 1, False),
    "andne.d": (1, 1, False),
    "andlt.s": (0, 2, False),
    "andlt.d": (1, 2, False),
    "andge.s": (0, 3, False),
    "andge.d": (1, 3, False),
    "oreq.s": (0, 4, False),
    "oreq.d": (1, 4, False),
    "orne.s": (0, 5, False),
    "orne.d": (1, 5, False),
    "orlt.s": (0, 6, False),
    "orlt.d": (1, 6, False),
    "orge.s": (0, 7, False),
    "orge.d": (1, 7, False),
    "andgt.s": (0, 2, True),
    "andgt.d": (1, 2, True),
    "andle.s": (0, 3, True),
    "andle.d": (1, 3, True),
    "orgt.s": (0, 6, True),
    "orgt.d": (1, 6, True),
    "orle.s": (0, 7, True),
    "orle.d": (1, 7, True),
}
# key: neumonic, value: (x, func)
sec5_dict = {
    "add": (0, 0),
    "and": (0, 2),
    "or": (0, 4),
    "xor": (0, 6),
    "nadd": (0, 1),
    "cand": (0, 3),
    "cor": (0, 5),
    "xnor": (0, 7),
    "andeq": (1, 0),
    "andne": (1, 1),
    "andlt": (1, 2),
    "andge": (1, 3),
    "andltu": (1, 4),
    "andgeu": (1, 5),
    "oreq": (1, 8),
    "orne": (1, 9),
    "orlt": (1, 10),
    "orge": (1, 11),
    "orltu": (1, 12),
    "orgeu": (1, 13),
    "min": (1, 14),
    "max": (1, 15),
    "minu": (1, 6),
    "maxu": (1, 7),
    "andgt": (1, 2),
    "andle": (1, 3),
    "andgtu": (1, 4),
    "andleu": (1, 5),
    "orgt": (1, 10),
    "orle": (1, 11),
    "orgtu": (1, 12),
    "orleu": (1, 13),
    "sel": (2, 0),
    "seln": (2, 1),
    "selp": (2, 2),
    "selz": (2, 0),
    "madd": (2, 4),
    "nmadd": (2, 5)
}

# func, x, n, swap
# FIXME: all values with None are place holders, THEY MUST BE REPLACED
sec4_ALU_dict = {
    "add": (0, 0, None, False),
    "nadd": (1, 0, None, False),
    "and": (2, 0, None, False),
    "cand": (3, 0, None, False),
    "or": (4, 0, None, False),
    "cor": (5, 0, None, False),
    "xor": (6, 0, None, False),
    "xnor": (7, 0, None, False),
    "eq": (8, 0, None, False),
    "ne": (9, 0, None, False),
    "lt": (10, 0, None, False),
    "ge": (11, 0, None, False),
    "ltu": (12, 0, None, False),
    "geu": (13, 0, None, False),
    "min": (14, 0, None, False),
    "max": (15, 0, None, False),
    "shl": (0, 0, None, False),
    "shr": (1, 1, None, False),
    "sar": (2, 1, None, False),
    "ror": (3, 1, None, False),
    "mul": (8, 1, None, False),
    "div": (12, 1, None, False),
    "mod": (13, 1, None, False),
    "divu": (14, 1, None, False),
    "modu": (15, 1, None, False),
    "adds": (None, 2, 'i4', False),
    "nadds": (None, 3, 'i4', False),
    "sub": (1, 0, None, True),
    "andc": (1, 0, None, True),
    "orc": (1, 0, None, True),
    "gt": (1, 0, None, True),
    "le": (1, 0, None, True),
    "gtu": (1, 0, None, True),
    "leu": (1, 0, None, True),
}

# : (opcode, d.func, imm)
sec4_ALUI_dict = {
    "add": (32, 0, 'i3'),
    "nadd": (32, 1, 'i3'),
    "and": (32, 2, 'i3'),
    "cand": (32, 3, 'i3'),
    "or": (33, 4, 'i3'),
    "cor": (33, 5, 'i3'),
    "xor": (33, 6, 'i3'),
    "set": (33, 7, 'i2'),
    "eq": (34, 8, 'i3'),
    "ne": (34, 9, 'i3'),
    "lt": (34, 10, 'i3'),
    "ge": (34, 11, 'i3'),
    "ltu": (35, 12, 'i3'),
    "geu": (35, 13, 'i3'),
    "min": (35, 14, 'i3'),
    "max": (35, 15, 'i3'),
    "sub": (32, 0, 'i3'),
    "andc": (32, 0, 'i3'),
    "orc": (33, 4, 'i3'),
    "xnor": (33, 6, 'i3'),
    "mov": (33, 4, 0),
    "neg": (32, 1, 0),
    "not": (33, 5, 0),
    "gt": (32, 0, 'i3'),
    "le": (32, 0, 'i3'),
    "gtu": (33, 4, 'i3'),
    "leu": (33, 4, 'i3'),
}

def asmtointsection2(d):
    # Compare with Zero Branches (Pseudo)
    if d.op in d.opcodes.get('bzero'):
        d.rai = reg(d.args[1])
        d.imm = 0

        if d.op == "blez" or d.op == "bgtz":
            d.imm = 1
        return d.rai, d.rbi, d.imm
    # Pseudo-Bd.rainches
    if d.op in {'ble': 10, 'bgt': 11, 'bgtu': 12, 'bleu': 13, }:
        d.rai = reg(d.args[1])
        d.imm = int(d.args[2]) + 1
        return d.rai, d.rbi, d.imm
    # Ret
    # Register-immediate Bd.ranches
    if 8 <= d.opcode <= 13:
        d.ra = d.args[1]

        d.rai = reg(d.ra)
        d.imm = int(d.args[2])  # p15 states this should be Ud.imm5
    # Register-Register Bd.ranch
    elif 16 <= d.opcode <= 21:
        d.ra = d.args[1]

        d.rai = reg(d.ra)
        d.rbi = reg(d.args[2])
        # loop or loopd or jalr
    elif d.opcode == 22 or d.opcode == 22 or d.opcode == 15:

        d.rb = d.args[2]
        d.rbi = reg(d.rb)

        d.ra = d.args[2]
        d.rai = reg(d.ra)
    elif d.opcode == 14:
        d.rai = reg(d.args[1])
    # return d.rai, d.rbi, d.imm

# d.ra, d.rbi, rc, d.rd, s, d.func, d.imm =
def asmtoint3(d):
    # sec3.6
    # d.opcodes, d.func = opcodes.get('ls').get(d.op)
    print(str(d.func))

    # Load I-Format
    if d.opcode == 24:
        d.rb = d.args[1]
        d.ra = d.args[2]
        d.imm = int(d.args[3])
    # Store I-Format
    elif d.opcode == 25:
        d.rb = d.args[3]
        d.ra = d.args[1]
        d.imm = int(d.args[2])
    # Loadx R-Format
    elif d.opcode == 26:
        d.rb = d.args[3]
        d.ra = d.args[2]
        d.rd = d.args[1]
        d.s = int(d.args[4])
    elif d.opcode == 27:  # loadx
        d.rb = d.args[2]
        d.ra = d.args[1]
        d.rc = d.args[4]
        d.s = int(d.args[3])

    # setting the register indexes
    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)
    if d.rc is not None:
        d.rci = reg(d.rc)
    if d.rd is not None:
        d.rdi = reg(d.rd)

    # return ra, d.rbi, rc, d.rdi, s, d.func, d.imm

# d.opcode, d.ra, d.rbi, d.func, d.imm
def asmtointALUI(d):
    d.rb = d.args[1]
    d.ra = d.args[2]

    d.rbi = int(d.b)
    d.rai = int(d.a)

    d.opcode, d.func, d.imm = translatedDictArgs(d, sec4_ALUI_dict[d.op])
    # return opcode, ra, d.rbi, func, imm

# d.opcode, d.ra, d.rbi, d.func, d.imm
def asmtointRET(d):
    d.opcode = 36

    d.ra = d.args[1]
    d.rb = d.args[2]

    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)

    d.func, d.imm = translatedDictArgs(d, sec4_RET_dict[d.op])

def translatedDictArgs(instr, tup: tuple):
    """
    returns the translate version of tup, but translate, example:
        (13, 'r2', 'i3', 'n'), returns (13, reg(instr.args[2]), instr.args[3], instr.n)
    :param instr:
    :param tup: the tuple to translate
    :return: a translated tuple, (maps 'i3' to args[3], ... etc)
    """
    l = list(tup)
    for i in range(len(l)):
        if type(l[i]) is str:
            match = re.search(r'^(\w+)(\d+)$'.lower(), l[i], re.IGNORECASE)
            if match and match.groups() and len(match.groups()):
                word = match.groups()[0]
                number = match.groups()[1]
                print("word={}, number={}".format(word, number))

                if word in ['i', 'args']:
                    l[i] = instr.args[int(number)]
                    if word == 'i':
                        l[i] = int(l[i])
                elif word == ['r']:  # if reg
                    l[i] = reg(l[i])
                elif hasattr(instr, l[i]):  # any property
                    l[i] = getattr(instr, l[i])

    return tuple(l)

# d.opcode, d.ra, d.rbi, d.func, d.imm_L, d.imm_R, d.imm
def asmtointSHIFT(d):
    d.opcode = 37

    d.rb = d.args[1]
    d.ra = d.args[2]
    d.rbi = reg(d.rb)
    d.rai = reg(d.ra)

    d.func, d.imm_L, d.imm_R, d.imm = translatedDictArgs(d, sec4_SHIFT_dict[d.op])

# d.opcode, d.ra, d.rbi, d.func, x, d.rd
def asmtointALU(d):
    d.opcode = 40

    d.rd = d.args[1]
    d.ra = d.args[2]
    d.rb = d.args[3]

    d.func, d.x, d.n, swap = translatedDictArgs(d, sec4_ALU_dict[d.op])
    if swap:
        d.ra, d.rb = d.rb, d.ra
    # swapping must be done before the registers are translated

    d.rdi = reg(d.rd)
    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)

# def asmtointALU(d):
#     """
#     Note that func and n both share the same variable func
#     :param args:
#     :return: (opcode, ra, rbi, func, x, rd)
#     """
#     d.opcode = 40
#     d.rdi = reg(d.args[1])
#     d.rai = reg(d.args[2])
#     d.rbi = reg(d.args[3])
#
#     # (func, x, n)
#     opcode40_dict = {
#         "add": (0, 0),
#         "nadd": (1, 0),
#         "and": (2, 0),
#         "cand": (3, 0),
#         "or": (4, 0),
#         "cor": (5, 0),
#         "xor": (6, 0),
#         "xnor": (7, 0),
#         "eq": (8, 0),
#         "ne": (9, 0),
#         "lt": (10, 0),
#         "ge": (11, 0),
#         "ltu": (12, 0),
#         "geu": (13, 0),
#         "min": (14, 0),
#         "max": (15, 0),
#         "shl": (0, 1),
#         "shr": (1, 1),
#         "sar": (2, 1),
#         "ror": (3, 1),
#         "mul": (8, 1),
#         "div": (12, 1),
#         "mod": (13, 1),
#         "divu": (14, 1),
#         "modu": (15, 1),
#
#         "adds": ("n", 2),  # n = 0 ~ 15
#         "nadds": ("n", 2),  # n = 0 ~ 15
#
#         "sub": (1, 0),  # uses nadd, swaps ra & d.rbi
#         "andc": (1, 0),  # uses cand, swaps ra & d.rbi
#         "orc": (1, 0),  # uses cor,  swaps ra & d.rb
#         "gt": (1, 0),  # uses lt,   swaps ra & d.rb
#         "le": (1, 0),  # uses ge,   swaps ra & d.rb
#         "gtu": (1, 0),  # uses ltu,  swaps ra & d.rbi
#         "leu": (1, 0),  # uses geu,  swaps ra & d.rbi
#     }
#
#     # Pseudo-Instructions for ALU
#     if d.op in ["sub", "andc", "orc", "gt", "le", "gtu", "leu"]:  # swap
#         d.ra, d.rbi = d.rbi, d.ra
#
#     d.func, d.x = opcode40_dict.get(d.op)
#     if d.func == "n":
#         d.func = int(d.args[2])


# d.opcode, d.ra, d.rd, d.func, d.p =
def asmtointFPU1(d):
    d.opcode = 42
    d.rdi = reg(d.args[1])
    d.rai = reg(d.args[2])
    d.p, d.func = fpu1_dict[d.op]

# d.opcode, d.ra, d.rbi, d.rd, d.func, d.p
def asmtointFPU2(d):
    d.opcode = 43

    d.rd = d.args[1]
    d.ra = d.args[2]
    d.rb = d.args[3]

    d.p, d.func, swp = fpu2_dict[d.op]
    if swp:
        d.ra, d.rb = d.rb, d.ra

    d.rdi = reg(d.rd)
    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)

# d.opcode, d.ra, d.rbi, rc, d.rd, d.func, d.p
def asmtointFPU3(d):
    d.opcode = 44
    if d.op == "min.d" or d.op == "max.d":
        d.opcode = 43

    d.rd = d.args[1]
    d.ra = d.args[2]
    d.rb = d.args[3]
    d.rc = d.args[4]

    d.p, d.func, swp = fpu3_dict[d.op]
    if swp:
        d.rc, d.rb = d.rb, d.rc

    d.rdi = reg(d.rd)
    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)
    d.rci = reg(d.rc)

    # return opcode, ra, rb, rc, rd, func, p

# opcode, ra, rb, rc, rd, func, x
def asmtoint5(d):
    d.opcode = 41

    d.rd = d.args[1]
    d.ra = d.args[2]
    d.rb = d.args[3]
    d.rc = d.args[4]

    d.x, d.func = sec5_dict[d.op]
    if d.op == "selz":  # sel , switch b and c
        d.rb, d.rc = d.rc, d.rd

    d.rdi = reg(d.rd)
    d.rai = reg(d.ra)
    d.rbi = reg(d.rb)
    d.rci = reg(d.rc)

def inttohex(d):
    d.calcLabelOffset()


    def twos_comp(val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val


    instruction = "0" * 32
    if d.opcode == 2 or d.opcode == 3:
        offsetstr = format(twos_comp(d.offset, 26), '026b')
        offsetstr = re.sub('^-', '', offsetstr)
        instruction = format(d.opcode, '06b') + offsetstr
    # Section 2 (branch d.imm)
    elif 8 <= d.opcode <= 13:
        immstr = format(d.imm, '05b')  # p15 states this should be Uimm5 is this the correct format???
        offsetstr = format(twos_comp(d.offset, 16), '016b')
        instruction = format(d.opcode, '06b') + format(d.rai, '05b') + immstr + offsetstr
    # JR instruction p15
    elif d.opcode == 14:
        rastr = format(d.rai, '05b')
        emptystr = format(0, '05b')
        offsetstr = format(twos_comp(d.offset, 16), '016b')
        instruction = format(d.opcode, '06b') + rastr + emptystr + offsetstr
    # Section2 (non d.imm branch)
    elif 15 <= d.opcode <= 23:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        offsetstr = format(twos_comp(d.offset, 16), '016b')
        instruction = opstr + rastr + format(d.rbi, '05b') + offsetstr
        # Section 3
    elif d.opcode == 24 or d.opcode == 25:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        funcstr = format(d.func, '04b')
        immstr = format(d.imm, '012b')
        instruction = opstr + rastr + rbstr + funcstr + immstr
    elif d.opcode == 26 or d.opcode == 27:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        funcstr = format(d.func, '04b')
        sstr = format(d.s, '02b')
        if d.opcode == 27:
            rdstr = format(0, '05b')
            rcstr = format(d.rci, '05b')
        else:
            rdstr = format(d.rdi, '05b')
            rcstr = format(0, '05b')
        instruction = opstr + rastr + rbstr + funcstr + sstr + rcstr + rdstr
    elif 32 <= d.opcode <= 36:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        instruction = opstr + rastr + rbstr + format(d.func, '04b') + format(d.imm, '12b')
    elif d.opcode == 37:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        if d.imm_L is None and d.imm_R is None and d.imm is not None:
            instruction = opstr + rastr + rbstr + format(d.func, '04b') + format(d.imm, '12b')
        elif d.imm_L and d.imm_R and d.imm is None:
            instruction = opstr + rastr + rbstr + format(d.func, '04b') + format(d.imm_L, '06b') + format(d.imm_R,
                                                                                                          '06b')
        elif d.imm_L and d.imm_R is None and d.imm is None:
            instruction = opstr + rastr + rbstr + format(d.func, '04b') + format(d.imm_L, '06b')
        elif d.imm_L is None and d.imm_R and d.imm is None:
            instruction = opstr + rastr + rbstr + format(d.func, '04b') + format(d.imm_R, '06b')
    elif d.opcode == 40:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        x_str = format(d.x, '02b')
        rdstr = format(d.imm, '05b')
        if d.x in [0, 1]:
            instruction = opstr + rastr + rbstr + format(d.func, '04b') + x_str + rdstr
        elif d.x in [2, 3]:
            instruction = opstr + rastr + rbstr + format(d.n, '04b') + x_str + rdstr
    elif d.opcode == 41:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        rbstr = format(d.rbi, '05b')
        funcstr = format(d.func, '04b')
        xstr = format(d.x, '02b')
        rcstr = format(d.rci, '05b')
        rdstr = format(d.rdi, '05b')
        instruction = opstr + rastr + rbstr + funcstr + xstr + rcstr + rdstr
        # FPU instructions
    elif d.opcode in [42, 43, 44]:
        opstr = format(d.opcode, '06b')
        rastr = format(d.rai, '05b')
        fnstr = format(d.func, '05b')
        pstr = format(d.p, '01b')
        rdstr = format(d.rdi, '05b')
        if d.opcode == 42:
            rbstr = format(0, '05b')
            rcstr = format(0, '05b')
        elif d.opcode == 43:
            rbstr = format(d.rbi, '05b')
            rcstr = format(0, '05b')
        else:
            rbstr = format(d.rbi, '05b')
            rcstr = format(d.rci, '05b')
        instruction = opstr + rastr + rbstr + fnstr + pstr + rcstr + rdstr
    else:
        opstr = format(d.opcode, '02b')
        rbstr = format(d.rbi, '03b')
        rastr = format(d.rai, '03b')
        if d.imm < 0:
            imm2s = ((-d.imm) ^ 255) + 1
            immstr = format(imm2s, '08b')
        else:
            immstr = format(d.imm, '08b')
        # print opstr, rtstr, rsstr, immstr
        instruction = opstr + rastr + rbstr + immstr
    instruction = re.sub('\s', '0',
                         instruction)  # replacing empty spaces, empty spaces appear when the bits are reserved
    return format(int(instruction, 2), '04x')

def asmtointNOP(d):
    # FIXME: this is a fake function
    return d.opcode, d.imm

def asmtoint(asm):
    from Addressable import Instruction
    if isinstance(asm, str):
        print("WARNING: Be careful, you just passed a string to asmtoint, you should pass an Instruction")
        return decodeInstruction(Instruction(asm))
    return decodeInstruction(asm)  # asm is actually an Instruction

def decodeInstruction(d):

    # Section 6 FPU1
    if d.op in fpu1_dict:
        if len(d.args) != 3:
            raise Exception('Incorrect Number of arguments')
        asmtointFPU1(d)
    # Section 6 FPU2
    elif d.op in fpu2_dict:
        # Check if common between fpu2 and fpu3
        if d.op in fpu3_dict:
            if len(d.args) == 4:
                asmtointFPU2(d)
            elif len(d.args) == 5:
                asmtointFPU3(d)
            else:
                raise Exception('Incorrect Number of arguments' + str(len(d.args)))
        elif len(d.args) != 4:
            raise Exception('Incorrect Number of arguments')
        asmtointFPU2(d)
    # Section 6 FPU3    
    elif d.op in fpu3_dict:
        if len(d.args) != 5:
            raise Exception(
                'Incorrect Number of arguments : ' + str(len(d.args)))
        asmtointFPU3(d)

    # SECTION 2 branches
    elif d.op in opcodes.get('b'):
        if len(d.args) != 4:
            raise Exception('Incorrect Number of arguments : ' + str(len(d.args)))
        # Check if user used immediate or register version of the instruction
        if d.args[2][0] != "r":
            d.op = d.op + "i"

        d.opcode = opcodes.get('b').get(d.op)
        d.label = d.args[3]
        d.ra, d.rbi, d.imm = asmtointsection2(d)
    elif d.op in opcodes.get('bzero'):
        if len(d.args) != 3:
            raise Exception('Incorrect Number of arguments : ' + str(len(d.args)))

        d.opcode = opcodes.get('b').get(d.op)
        d.label = d.args[2]
        d.ra, d.rbi, d.imm = asmtointsection2(d)
    # SECTION 2 j type (does not call asmtointsection2)
    elif d.op in opcodes.get('j'):
        if d.op == "jal" or d.op == "j":
            d.label = d.args[1]
        elif d.op == "jr":
            if len(d.args) == 3:
                d.label = d.args[2]
            elif len(d.args) == 2:
                d.offset = 0
            else:
                raise Exception(
                    'Incorrect Number of arguments : ' + str(len(d.args)))
            d.ra = int(d.args[1])
        elif d.op == "jalr":
            if len(d.args) == 4:
                label = d.args[3]
            elif len(d.args) == 3:
                d.offset = 0
            else:
                raise Exception('Incorrect Number of arguments : ' + str(len(d.args)))
            d.ra = reg(d.args[2])
            d.rbi = reg(d.args[1])
        elif d.op == "ret":
            if len(d.args) != 1:
                raise Exception(
                    'Incorrect Number of arguments : ' + str(len(d.args)))
            d.offset = 0
            d.ra = 31
        d.opcode = opcodes.get('j').get(d.op)
    # Section 3
    elif d.op in opcodes.get('ls'):
        d.opcode, d.func = opcodes.get('ls').get(d.op)
        # Check if it is R-Format (has 5 arguments)
        if len(d.args) == 5:  # convertng I to R type (P21)
            d.opcode += 2
        if len(d.args) != 5 and len(d.args) != 4:
            raise Exception('Incorrect Number of arguments : ' + str(len(d.args)))
        asmtoint3(d)
    # Section 4
    # Checking if it belongs to ALUI (Opcode 32 - 35)
    elif len(d.args) == 5 and d.op in sec4_ALUI_dict:
        if len(d.args) != 5:
            asmtointALUI(d)

    # Checking if it belongs to RET (Opcode 36)
    elif d.op in sec4_RET_dict:
        print(d.op)
        if (len(d.args) != 4) and d.op != "xnor" and d.op != "cor":  # XNOR is in section 5 and contains 5 arguments
            raise Exception('Incorrect Number of arguments')
        if len(d.args) == 4:  # This line exists to not include section5 xnor
            asmtointRET(d)
    # Checking if it belongs to NOP (Opcode 0)         ############## REVIEW, I have done nothing with this NOP
    elif d.op == "orc":
        if len(d.args) != 2:
            raise Exception('Incorrect Number of arguments')
        asmtointNOP(
            d)  # FIXME: IDK what this is supposed to be [Rakan: i left it here so that we don't forget about it in the simulator]
    # Checking if it belongs to SHIFT (Opcode 37)
    # FIXME:
    elif d.op in sec4_SHIFT_dict:
        if len(d.args) != 4:
            raise Exception('Incorrect Number of arguments')
        asmtointSHIFT(d)

    # Checking if it belongs to ALU (Opcode 40)
    elif len(d.args) == 4 and d.op in sec4_ALU_dict:
        # FIXME: WHY does it have to be length 4 when adds and nadds has a length of 3?!!!
        if len(d.args) != 4 and d.op != "min" and d.op != "max":
            raise Exception('Incorrect Number of arguments')
        asmtointALU(d)
    # Section 5 Opcode 41
    elif d.op in opcodes.get('alu'):
        if len(d.args) != 5 and len(d.args) != 4:
            raise Exception("Incorrect Number of parameters passed")
        if len(d.args) == 5:
            asmtoint5(d)
    else:
        print("Returning all zeroes since the instruction is not recognized")

        for attr in ['opcode', 'ra', 'rb', 'rc', 'rd', 'func', 'imm', 'p', 'offset', 's', 'x', 'n', 'imm_L', 'imm_R']:
            setattr(d, attr, 0)

        return d  # this is the default/NOP case
    # opcode 41
    # This is not elif statement because it shares instruction __names__ with previous elif statements
    if d.op in opcodes.get('alu'):
        if len(d.args) != 5 and len(d.args) != 4:
            raise Exception("Incorrect Number of parameters passed")
        if len(d.args) == 5:
            asmtoint5(d)
    return d

def decodeToHex(asm):
    """
    string line to hex string
    """
    d = asmtoint(asm)
    print(str(asm) + " -> " + str(d))
    return inttohex(d)

def reg(mnemonic: str):
    """
    given the neumonic (example: $0, $zero, $r1, $v0, etc...)
    :param mnemonic:
    :return: register number, or None if doesn't exist
    """
    if type(mnemonic) is not str:
        return None
        # raise Exception("mnemonic must be a string:", mnemonic)

    # (key: mnemonic, value: registerNumber)
    registerAliasDict = {
        '$zero': 0b00000,
        '$at': 0b00001,
        '$v0': 0b00010,
        '$v1': 0b00011,
        '$a0': 0b00100,
        '$a1': 0b00101,
        '$a2': 0b00110,
        '$a3': 0b00111,
        '$t0': 0b01000,
        '$t1': 0b01001,
        '$t2': 0b01010,
        '$t3': 0b01011,
        '$t4': 0b01100,
        '$t5': 0b01101,
        '$t6': 0b01110,
        '$t7': 0b01111,
        '$s0': 0b10000,
        '$s1': 0b10001,
        '$s2': 0b10010,
        '$s3': 0b10011,
        '$s4': 0b10100,
        '$s5': 0b10101,
        '$s6': 0b11000,
        '$s7': 0b10111,
        '$t8': 0b11000,
        '$t9': 0b11001,
        '$k0': 0b11010,
        '$k1': 0b11011,
        '$gp': 0b11100,
        '$sp': 0b11101,
        '$fp': 0b11110,
        '$ra': 0b11111,
    }

    if mnemonic[0].lower() == 'r':
        return int(mnemonic[1:])
    else:
        if mnemonic in registerAliasDict:
            return registerAliasDict.get(mnemonic, 0)
