import Assembler
import re

"""
Conventions:
For registers, we keep the register mnemonic,
"""


class Addressable:
    __nextUnallocated__ = 0  # static field, keeps track of last available unallocated address


    # __globalAddressTable__: dict  # stores every single `Addressable` object

    def __init__(self, size=4, startAddress=-1, lineStr='', enforceAlignment=True):
        """
        :param size: number of bytes to allocate
        :param start: optional - if not indicated,
        will choose the next unallocated memory address
        """

        if startAddress == -1:
            startAddress = Addressable.__nextUnallocated__
        if enforceAlignment:
            startAddress = Addressable.__align__(startAddress, size)

        self.address: int = startAddress  # the start address
        self.addressEnd: int = self.address + size  #
        self.lineStr: str = lineStr  # [optional] the line from the source file that this corresponds to

        # update the pointer
        if Addressable.__nextUnallocated__ <= self.addressEnd:
            Addressable.__nextUnallocated__ = self.addressEnd + 1


    @staticmethod
    def __align__(offset, align) -> int:  # returns the address to start with
        padding = (align - (offset % align)) % align
        return offset + padding


    @staticmethod
    # splits the line and removes unwanted symbols
    def __splitLine__(line: str) -> list:  # return args/args
        import re
        regex = re.compile(r"[,\s()=\[|\]]+")
        args = [arg for arg in re.split(regex, line) if arg != ""]

        for x in args:
            if re.search(r'[^\w\d.\-]', x):
                raise Exception('Invalid character encountered:', line)

        return args


    def size(self) -> int:
        """ :return: size of addressable in bytes """
        return self.addressEnd - self.address


class DataBlock(Addressable):
    def __init__(self, data, *args):
        super(DataBlock, self).__init__(args)  # instantiate a normal Addressable
        self.data = data


class Instruction(Addressable):
    def __init__(self, lineStr, address=-1):
        super(Instruction, self).__init__(size=1, startAddress=address, lineStr=lineStr)

        asmLine = lineStr.split('//')[0].strip()

        regex = re.compile(r"[,\s()=\[|\]]+")

        args = [arg for arg in (re.split(regex, asmLine)) if arg != ""]
        for x in args:
            if re.search(r'[^\w\d.\-]', x):
                raise Exception('Invalid character encountered:', asmLine)

        self.asmLine = asmLine

        self.type = self.getType()

        self.args = Instruction.__splitLine__(lineStr)
        self.op = self.args[0]
        self.rd: str = None
        self.ra: str = None
        self.rb: str = None
        self.rc: str = None

        # decode fields
        self.opcode: int = None
        self.func: int = None

        self.rdi: int = None
        self.rai: int = None
        self.rbi: int = None
        self.rci: int = None

        self.imm: int = 0
        self.p: int = None
        self.x: int = None
        self.s: int = None
        self.n: int = None
        self.imm_L: int = None
        self.imm_R: int = None
        self.offset: int = None

        Assembler.decodeInstruction(self)


    # TODO: these should be moved to the Assembler
    sections = {
        2: {
            2,
            3,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23
        },
        3: {
            24,
            25,
            26,
            27
        },
        5: {
            41,
        }
    }


    def hex(self) -> str:
        # returns the hex string
        return Assembler.decodeToHex(self)


    def getType(self) -> str:
        pass


    def getFormat(self) -> str:
        pass


    def __str__(self):
        s = ""
        attrs = ['opcode', 'ra', 'rb', 'rc', 'rd', 'func', 'imm', 'p', 'offset', 's', 'x', 'n', 'imm_L', 'imm_R']
        for attr in attrs:
            s += ", " + attr + ": "
            if hasattr(self, attr):
                s += str(getattr(self, attr))
        return s


    def execute(self, sim):
        opcode = self.opcode
        if opcode in Instruction.sections[2]:
            pass  # do
        elif opcode in Instruction.sections[3]:
            rai = self.ra
            rbi = self.rb
            if opcode in {24, 25}:
                imm = self.imm
                if opcode == 24:
                    if self.func == 0:  # LBU
                        pass  # do
                    elif self.func == 1:  # LHU
                        pass  # do
                    elif self.func == 2:  # LWU
                        pass  # do
                    elif self.func == 3:  # LDU
                        pass  # do
                    elif self.func == 4:  # LB
                        pass  # do
                    elif self.func == 5:  # LH
                        pass  # do
                    elif self.func == 6:  # LW
                        pass  # do
                    elif self.func == 7:  # LD
                        pass  # do
                elif opcode == 25:
                    if self.func == 0:  # SB
                        pass  # do
                    elif self.func == 1:  # SH
                        pass  # do
                    elif self.func == 2:  # SW
                        pass  # do
                    elif self.func == 3:  # SD
                        pass  # do
            elif opcode == 26:  # LoadX
                s = self.s
                rd = self.rd
                if self.func == 0:  # LBU
                    pass  # do
                elif self.func == 1:  # LHU
                    pass  # do
                elif self.func == 2:  # LWU
                    pass  # do
                elif self.func == 3:  # LDU
                    pass  # do
                elif self.func == 4:  # LB
                    pass  # do
                elif self.func == 5:  # LH
                    pass  # do
                elif self.func == 6:  # LW
                    pass  # do
                elif self.func == 7:  # LD
                    pass  # do
            elif opcode == 27:
                s = self.s
                rc = self.rc
                if self.func == 0:  # SB
                    pass  # do
                elif self.func == 1:  # SH
                    pass  # do
                elif self.func == 2:  # SW
                    pass  # do
                elif self.func == 3:  # SD
                    pass  # do
        elif opcode in Instruction.sections[4]:  # i need to distinguish between the duplicated instructions in here
            rai = self.ra  # Also: remember the NOP
            rbi = self.rb  # '?' means a part i don't know how to do
            imm = self.imm
            # this is also p (same postion, same number of bits)

            # FUNCTION FOR SIGIN EXTEND
            # def sign_extend(value, bits):
            #    sign_bit = 1 << (bits - 1)
            #    return (value & (sign_bit - 1)) - (value & sign_bit)

            # for opcode 32 - 35
            if opcode in {32, 33, 34, 45}:  # Rb is the destination here
                if self.func == 0:  # ADD   [sign extend imm to 64 bits]
                    rbi = rai + imm
                elif self.func == 1:  # NADD  [sign extend imm to 64 bits]
                    rbi = -rai + imm
                elif self.func == 2:  # AND   [sign extend imm to 64 bits]
                    rbi = rai & imm
                elif self.func == 3:  # CAND  [sign extend imm to 64 bits]
                    rbi = ~rai & imm
                elif self.func == 4:  # OR    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = rai | imm
                elif self.func == 5:  # COR   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = ~rai | imm
                elif self.func == 6:  # XOR   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = rai ^ imm
                elif self.func == 7:  # SET   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = imm
                elif self.func == 8:  # EQ    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = (rai == imm)
                elif self.func == 9:  # NE    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = (rai != imm)
                elif self.func == 10:  # LT    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rbi = (rai < imm)
                elif self.func == 11:  # GE    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rbi = (rai > imm)
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rbi = (rai < imm)
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rbi = (rai > imm)
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    rbi = min(rai, imm)
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    rbi = max(rai, imm)

            elif opcode == 36:  # same as above but with return Example: RETOP Rb = Ra, Imm12 // JR R31; OP Rb = Ra, Imm12 
                if self.func == 0:  # ADD   [sign extend imm to 64 bits]
                    rbi = rai + imm
                elif self.func == 1:  # NADD  [sign extend imm to 64 bits]
                    rbi = -rai + imm
                elif self.func == 2:  # AND   [sign extend imm to 64 bits]
                    rbi = rai & imm
                elif self.func == 3:  # CAND  [sign extend imm to 64 bits]
                    rbi = ~rai & imm
                elif self.func == 4:  # OR    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = rai | imm
                elif self.func == 5:  # COR   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = ~rai | imm
                elif self.func == 6:  # XOR   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = rai ^ imm
                elif self.func == 7:  # SET   [sign extend imm to 64 bits & use 1 NOP]
                    rbi = imm
                elif self.func == 8:  # EQ    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = (rai == imm)
                elif self.func == 9:  # NE    [sign extend imm to 64 bits & use 1 NOP]
                    rbi = (rai != imm)
                elif self.func == 10:  # LT    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rbi = (rai < imm)
                elif self.func == 11:  # GE    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rbi = (rai > imm)
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rbi = (rai < imm)
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rbi = (rai > imm)
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    rbi = min(rai, imm)
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    rbi = max(rai, imm)




            # for Opcode 37 SHIFT
            elif opcode == 37:
                if self.func == 0:  # SHLR
                    rbi = ((rai << self.imm_L) >> self.imm_R)
                elif self.func == 1:  # SHLR
                    rbi = ((rai << self.imm_L) >> self.imm_R)
                elif self.func == 2:  # SALR
                    rbi = rai & imm
                elif self.func == 3:  # ROR  [ not sure about how to rotate bitwise ]
                    pass  # do
                elif self.func == 8:  # MUL  [ im not sure why there is a MUL in the SHIFT section, IT'S NOT EVEN EXPLAINED! ]
                    pass  # do
                elif self.func == 12:  # DIV  [ SAME ]
                    pass  # do
                elif self.func == 13:  # MOD  [ SAME ]
                    pass  # do
                elif self.func == 14:  # DIVU [ SAME ]
                    pass  # do
                elif self.func == 15:  # MODU [ SAME ]
                    pass  # do


            # for opcode 40
            elif opcode == 40:
                if self.x == 0:
                    if self.func == 0:  # ADD
                        rd = rai + rbi
                    elif self.func == 1:  # NADD
                        rd = -rai + rbi
                    elif self.func == 2:  # AND
                        rd = rai & rbi
                    elif self.func == 3:  # CAND
                        rd = ~rai & rbi
                    elif self.func == 4:  # OR
                        rd = rai | rbi
                    elif self.func == 5:  # COR
                        rd = ~rai | rbi
                    elif self.func == 6:  # XOR
                        rd = rai ^ rbi
                    elif self.func == 7:  # XNOR
                        rd = ~rai ^ rbi
                    elif self.func == 8:  # EQ
                        rd = (rai == rbi)
                    elif self.func == 9:  # NE
                        rd = (rai != rbi)
                    elif self.func == 10:  # LT  [signed]?
                        rd = (rai < rbi)
                    elif self.func == 11:  # GT  [signed]?
                        rd = (rai > rbi)
                    elif self.func == 12:  # LTU [unsigned]?
                        rd = (rai < rbi)
                    elif self.func == 13:  # GTU [unsigned]?
                        pass  # do
                    elif self.func == 14:  # MIN
                        rd = min(rai, rbi)
                    elif self.func == 15:  # MAX
                        rd = max(rai, rbi)
                elif self.x == 2:
                    if self.func == 0:  # SHL
                        rd = (rbi << rai)
                    elif self.func == 1:  # SHR
                        rd = (rbi >> rai)
                    elif self.func == 2:  # SAR [ Shift to the right arithmetic, meaning: SIGNED]?
                        rd = (rbi << rai)
                    elif self.func == 3:  # ROR [ not sure how to rotate bitwise ]
                        pass  # do
                    elif self.func == 8:  # MUL [signed]?
                        rd = rai * rbi
                    elif self.func == 12:  # DIV [signed]?
                        rd = rai // rbi
                    elif self.func == 13:  # MOD [signed]?
                        rd = rai % rbi
                    elif self.func == 14:  # DIVU [unsigned]?
                        rd = rai // rbi
                    elif self.func == 15:  # MODU [unsigned]?
                        rd = rai % rbi
                elif self.x == 3:  # ADDS  Rd = Ra + Rb<<n
                    rd = rai + (rbi << self.n)
                elif self.x == 4:  # NADDS Rd = -Ra + Rb<<n
                    rd = -rai + (rbi << self.n)


        elif opcode in Instruction.sections[5]:
            rai = self.ra
            rbi = self.rb
            rc = self.rc
            rd = self.rd
            x = self.x
            if x == 0:
                if self.func == 0:
                    sim.regfile[rd] = sim.regfile[rai] + sim.regfile[rbi] + sim.regfile[rbi]
                elif self.func == 1:
                    pass  # do
                elif self.func == 2:
                    pass  # do
                elif self.func == 3:
                    pass  # do
                elif self.func == 4:
                    pass  # do
                elif self.func == 5:
                    pass  # do
                elif self.func == 6:
                    pass  # do
                elif self.func == 7:
                    pass  # do
            elif x == 1:
                if self.func == 0:
                    pass  # do
                elif self.func == 1:
                    pass  # do
                elif self.func == 2:
                    pass  # do
                elif self.func == 3:
                    pass  # do
                elif self.func == 4:
                    pass  # do
                elif self.func == 5:
                    pass  # do
                elif self.func == 6:
                    pass  # do
                elif self.func == 7:
                    pass  # do
                elif self.func == 8:
                    pass  # do
                elif self.func == 9:
                    pass  # do
                elif self.func == 10:
                    pass  # do
                elif self.func == 11:
                    pass  # do
                elif self.func == 12:
                    pass  # do
                elif self.func == 13:
                    pass  # do
                elif self.func == 14:
                    pass  # do
                elif self.func == 15:
                    pass  # do
            elif x == 2:
                if self.func == 0:
                    pass  # do
                elif self.func == 1:
                    pass  # do
                elif self.func == 2:
                    pass  # do
                elif self.func == 4:  # 3 is skipped according to doc
                    pass  # do
                elif self.func == 5:
                    pass  # do
        elif opcode in Instruction.sections[6]:
            pass  # do
            # # single precision fp
            # if self.p == 1:
            #
            # else:
            #     sim.regs[self.rd] = sim.regs[self.ra] + sim.regs[self.rb]


    def __asInt__(self) -> (int, int, int):
        pass
