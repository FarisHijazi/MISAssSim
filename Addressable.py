import Assembler
import MainProgram as sim

"""
Conventions:
For registers, we keep the register mnemonic,
"""


class Addressable:
    __nextUnallocated__ = 0  # static field, keeps track of last available unallocated address
    # __globalAddressTable__: dict  # stores every single `Addressable` object


    def __init__(self, size=1, startAddress=-1, lineStr='', enforceAlignment=True):
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
    def __splitLine__(line: str) -> list: # return args/args
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
        self.sim = sim  # the simulator instance
        self.type = self.getType()

        self.args = Instruction.__splitLine__(lineStr)
        self.op = self.args[0]
        self.rd: str
        self.ra: str
        self.rb: str
        self.rc: str

        # decode fields
        self.opcode: int
        self.func: int

        self.rdi: int
        self.rai: int
        self.rbi: int
        self.rci: int

        self.imm: int = 0
        self.p: int
        self.x: int
        self.s: int
        self.n: int
        self.imm_L: int
        self.imm_R: int
        self.offset: int

        self.operands: list  # list of operands


    # TODO: these should be moved to the Assembler
    sections = {}
    sections[3] = {
        24,
        25,
        26,
        27
    }
    sections[5] = {
        41,
    }


    def asHex(self) -> str:
        pass


    def decode(self):
        return Assembler.decode(self)


    def getType(self) -> str:
        pass


    def getFormat(self) -> str:
        pass


    def execute(self):
        opcode = self.opcode
        if opcode in Instruction.sections[2]:
            pass  # do
        elif opcode in Instruction.sections[3]:
            ra = self.ra
            rb = self.rb
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
        elif opcode in Instruction.sections[4]:
            pass  # do
        elif opcode in Instruction.sections[5]:
            ra = self.ra
            rb = self.rb
            rc = self.rc
            rd = self.rd
            x = self.x
            if x == 0:
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
