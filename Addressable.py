import re
import math

"""
Conventions:
For registers, we keep the register mnemonic,
"""


# FUNCTION FOR SIGIN EXTEND
def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


class Addressable:
    __nextUnallocated__ = 0  # static field, keeps track of last available unallocated address


    def __init__(self, size=4, startAddress=-1, lineStr='', alignment='auto'):
        """
        :param size: number of bytes to allocate
        :param start: optional - if not indicated,
        will choose the next unallocated memory address
        """

        if startAddress == -1:
            startAddress = Addressable.__nextUnallocated__

        if alignment == 'auto' or alignment is True:  # choose depending on the size
            alignment = size
            startAddress = Addressable.__align__(startAddress, alignment)

        self.address: int = startAddress  # the start address
        self.addressEnd: int = self.address + size  #
        self.lineStr: str = lineStr  # [optional] the line from the source file that this corresponds to

        # update the pointer
        if Addressable.__nextUnallocated__ <= self.addressEnd:
            Addressable.__nextUnallocated__ = self.addressEnd + 1


    @staticmethod
    def __align__(offset, align) -> int:  # returns the address to start with
        if align < 1:
            align = 1
        padding = (align - (offset % align)) % align
        return offset + padding


    @staticmethod
    # splits the line and removes unwanted symbols
    def __splitLine__(line: str) -> list:  # return args/args
        import re
        regex = re.compile(r"[,\s()=\[|\]]+")
        args = [arg for arg in re.split(regex, line) if arg != ""]

        for x in args:
            if re.search(r'[^\w\d.@\-]', x):
                raise Exception('Invalid character encountered:', line)

        return args


    def size(self) -> int:
        """ :return: size of addressable in bytes """
        return self.addressEnd - self.address


    def __str__(self):
        return "Addressable: ({}, {})".format(self.address, self.addressEnd)


    def __repr__(self):
        return self.__str__()


class DataBlock(Addressable):
    directives = {
        '.byte': 1,
        '.hword': 2,
        '.word': 4,
        '.dword': 8
    }


    def __init__(self, *args, **kwargs):
        super(DataBlock, self).__init__(**kwargs)  # instantiate a normal Addressable

        label, dataDirective, directiveArgs = DataBlock.parseDataSegmentLine(self.lineStr)

        if len(directiveArgs) == 0 or not dataDirective:
            raise Exception('ERROR: data segment values missing on line: "{}"'.format(self.lineStr))

        size = DataBlock.directives.get(dataDirective)

        datas = [DataBlock.parseData(arg, size) for arg in directiveArgs]

        self.data = datas


    # returns the value, as an array of bytes
    @staticmethod
    def parseData(arg: str, size_in_bytes):
        """
        :param arg: an element from the data array, example: 'A'
        :return: bytearray
        """
        arg = arg.strip()
        if arg[0] == arg[-1] == "'":  # single quotes
            return bytearray(arg[1:-1], 'asci')
        elif arg[0] == arg[-1] == '"':  # null terminated
            return bytearray(arg[1:-1] + '\0', 'asci')
        # elif not re.search(r'[^+\-\d]', arg): # if numbers only
        else:  # FIXME: this is just quickly for testing
            # ([\da-fbohx_.\-+,]+)(:([\da-fbohx.\s\-+,]+))?
            return bytearray(int(arg))


    @staticmethod
    def parseDataSegmentLine(lineStr: str):
        """
        :param lineStr:
        :return: (label:str, dataDirective: str, directiveArgs:list)
        """
        import re
        """
        Match 2
        Full match |         | @var2 .hword 0xABCD:10
        Group 1.   |         | @var2 
        Group 2.   | label   | @var2
        Group 3.   |         | .hword 
        Group 4.   | dataDir | .hword
        Group 5.   |  args   | 0xABCD:10
        Group 6.   |         | 
        """

        # https://regex101.com/library/bHWXO5
        matches = re.search(
            r"((@[\w\d][\w\d_]+)\s+)?"  # label
            r"((" + "|".join(DataBlock.directives.keys()) + r"+)\s+)?"  # directive
                                                            r"(\'.+\'|\".+\"|[\da-fbohx.\s\-+:\'\",_]+)"  # args (the data array)
                                                            r"(//.+|$|\s)+",  # terminator
            lineStr, re.IGNORECASE
        )

        if matches:
            # print("Match was found at {start}-{end}: {match}".format(start=matches.start(), end=matches.end(),
            #                                                          match=matches.group()))
            group_mapping = {
                2: 'label',
                4: 'dataDirective',
                5: 'args'
            }
            result = regexGetGroups(matches, group_mapping)
            print('regexGetGroups', result)

            label = None
            dataDirective = None
            args = None
            for groupNum in range(1, len(matches.groups()) + 1):
                if groupNum == 2:
                    label = matches.group(groupNum)
                if groupNum == 4:
                    dataDirective = matches.group(groupNum)
                if groupNum == 5:
                    args = matches.group(groupNum)

            # TODO: limitation: splitting on ',' means that if a string contains it, it will be split, no , allowed
            return label, dataDirective, args.split(',')


def regexGetGroups(matches, groupsMapping: dict):
    """
    :param matches:
    :param groupsMapping: {groupNumber: groupName}
    :return:
    """
    import re
    """
    Match 2
    Full match |         | @var2 .hword 0xABCD:10
    Group 1.   |         | @var2 
    Group 2.   | label   | @var2
    Group 3.   |         | .hword 
    Group 4.   | dataDir | .hword
    Group 5.   |  args   | 0xABCD:10
    Group 6.   |         | 
    """
    # {'groupName': string}
    results_dict = {}

    for groupNum in range(1, len(matches.groups()) + 1):
        if groupNum in groupsMapping:
            results_dict[groupsMapping.get(groupNum)] = matches.group(groupNum)

    return results_dict


class Instruction(Addressable):
    count = 0


    def __init__(self, lineStr, address=-1, symbolTable=None):
        super(Instruction, self).__init__(size=5, startAddress=address, lineStr=lineStr)

        asmLine = lineStr.split('//')[0].strip()

        self.asmLine = asmLine
        self.symbolTable = symbolTable

        self.type = self.getType()

        self.args = Instruction.__splitLine__(lineStr)
        self.op = self.args[0]
        self.rd: str = None
        self.ra: str = None
        self.rb: str = None
        self.rc: str = None

        # decode fields = None
        self.opcode: int = None
        self.func: int = None

        self.rdi: int = None
        self.rai: int = None
        self.rbi: int = None
        self.rci: int = None

        self.imm: int = None
        self.p: int = None
        self.x: int = None
        self.s: int = None
        self.n: int = None
        self.imm_L: int = None
        self.imm_R: int = None
        self.offset: int = None

        self.label: str = None

        from Assembler import decodeInstruction
        try:
            decodeInstruction(self)
        # except Exception as e:
        finally:
            print('ERROR: while decoding instruction: "{}, args: {}, {}"'.format(lineStr, self.args, self))

        Instruction.count += 1  # static counter


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
            27,
        },
        4: {
            32,
            33,
            34,
            35,
            36,
            37,
            40,
        },
        5: {
            41,
        },
        6: {
            42,
            43,
            44,
        },
    }


    def calcLabelOffset(self):
        if not self.label and not self.offset:
            # not a control flow instruction
            return

        for base in [10, 8, 16, 2]:
            try:
                self.offset = int(self.offset, base=base)
            except:
                pass

        if not self.symbolTable:
            raise Exception(
                "ERROR: decoding control flow instructions requires a symbol table to be passed to decodeInstruction()")

        if self.label in self.symbolTable:
            self.offset = self.symbolTable.get(self.label, 0).address - self.address >> 5
            print('calculated "{}" label offset: {}'.format(self.label, self.offset))


    def hex(self) -> str:
        # returns the hex string
        from Assembler import decodeToHex
        return decodeToHex(self)


    def getType(self) -> str:
        pass


    def getFormat(self) -> str:
        pass


    def __str__(self):
        d = {}
        for attr in ['opcode', 'ra', 'rb', 'rc', 'rd', 'func', 'imm', 'p', 'offset', 's', 'x', 'n', 'imm_L', 'imm_R']:
            # d[attr] = None
            if getattr(self, attr) is not None:
                d[attr] = getattr(self, attr)
        return str(d)


    def execute(self, sim):
        if self.opcode in Instruction.sections[2]:
            pass  # do
        elif self.opcode in Instruction.sections[3]:
            if self.opcode in {24, 25}:
                if self.opcode == 24:
                    if self.func == 0:  # LBU
                        pass  # do
                    elif self.func == 1:  # LHU
                        pass  # do
                    elif self.func == 2:  # LWU
                        pass  # do
                    elif self.func == 3:  # LDU
                        pass  # do
                    elif self.func == 4:  # LB
                        index = sim.regfile.get(self.rai) + self.imm
                        binaryString = sim.mem.theBytes[index]
                        print("Binary String : " + binaryString)
                        sim.regfile.set(self.rbi, int(binaryString, 2))
                    elif self.func == 5:  # LH
                        index = sim.regfile.get(self.rai) + self.imm
                        binaryString = sim.mem.theBytes[index]
                        binaryString1 = sim.mem.theBytes[index + 1]
                        finalString = binaryString + binaryString1
                        sim.regfile.set(self.rbi, int(finalString, 2))
                    elif self.func == 6:  # LW
                        index = sim.regfile.get(self.rai) + self.imm
                        binaryString = sim.mem.theBytes[index]
                        binaryString1 = sim.mem.theBytes[index + 1]
                        binaryString2 = sim.mem.theBytes[index + 2]
                        binaryString3 = sim.mem.theBytes[index + 3]
                        finalString = binaryString + binaryString1 + binaryString2 + binaryString3
                        sim.regfile.set(self.rbi, int(finalString, 2))
                    elif self.func == 7:  # LD
                        index = sim.regfile.get(self.rai) + self.imm
                        binaryString = sim.mem.theBytes[index]
                        binaryString1 = sim.mem.theBytes[index + 1]
                        binaryString2 = sim.mem.theBytes[index + 2]
                        binaryString3 = sim.mem.theBytes[index + 3]
                        binaryString4 = sim.mem.theBytes[index + 4]
                        binaryString5 = sim.mem.theBytes[index + 5]
                        binaryString6 = sim.mem.theBytes[index + 6]
                        binaryString7 = sim.mem.theBytes[index + 7]
                        finalString = binaryString + binaryString1 + binaryString2 + binaryString3 + binaryString4 + binaryString5 + binaryString6 + binaryString7
                        sim.regfile.set(self.rbi, int(finalString, 2))
                elif self.opcode == 25:
                    if self.func == 0:  # SB
                        rValue = sim.regfile.get(self.rbi)
                        rValueBin = format(rValue, '064b')
                        index = sim.regfile.get(self.rai) + self.imm
                        sim.mem.theBytes[index] = rValueBin[56:64]
                    elif self.func == 1:  # SH
                        rValue = sim.regfile.get(self.rbi)
                        rValueBin = format(rValue, '064b')
                        index = sim.regfile.get(self.rai) + self.imm
                        sim.mem.theBytes[index + 1] = rValueBin[56:64]
                        sim.mem.theBytes[index] = rValueBin[48:56]
                    elif self.func == 2:  # SW
                        rValue = sim.regfile.get(self.rbi)
                        rValueBin = format(rValue, '064b')
                        index = sim.regfile.get(self.rai) + self.imm
                        sim.mem.theBytes[index + 3] = rValueBin[56:64]
                        sim.mem.theBytes[index + 2] = rValueBin[48:56]
                        sim.mem.theBytes[index + 1] = rValueBin[40:48]
                        sim.mem.theBytes[index] = rValueBin[32:40]
                    elif self.func == 3:  # SD
                        rValue = sim.regfile.get(self.rbi)
                        rValueBin = format(rValue, '064b')
                        index = sim.regfile.get(self.rai) + self.imm
                        sim.mem.theBytes[index + 7] = rValueBin[56:64]
                        sim.mem.theBytes[index + 6] = rValueBin[48:56]
                        sim.mem.theBytes[index + 5] = rValueBin[40:48]
                        sim.mem.theBytes[index + 4] = rValueBin[32:40]
                        sim.mem.theBytes[index + 3] = rValueBin[24:32]
                        sim.mem.theBytes[index + 2] = rValueBin[16:24]
                        sim.mem.theBytes[index + 1] = rValueBin[8:16]
                        sim.mem.theBytes[index] = rValueBin[0:8]
            elif self.opcode == 26:  # LoadX
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
            elif self.opcode == 27:
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
        elif self.opcode in Instruction.sections[4]:  # i need to distinguish between the duplicated instructions in here
            # for self.opcode 32 - 35
            if self.opcode in [32, 33, 34, 45]:  # Rb is the destination here
                if self.func == 0:  # ADD   [sign extend imm to 64 bits]
                    self.rbi = self.rai + self.imm
                elif self.func == 1:  # NADD  [sign extend imm to 64 bits]
                    self.rbi = -self.rai + self.imm
                elif self.func == 2:  # AND   [sign extend imm to 64 bits]
                    self.rbi = self.rai & self.imm
                elif self.func == 3:  # CAND  [sign extend imm to 64 bits]
                    self.rbi = ~self.rai & self.imm
                elif self.func == 4:  # OR    [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = self.rai | self.imm
                elif self.func == 5:  # COR   [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = ~self.rai | self.imm
                elif self.func == 6:  # XOR   [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = self.rai ^ self.imm
                elif self.func == 7:  # SET   [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = self.imm
                elif self.func == 8:  # EQ    [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = (self.rai == self.imm)
                elif self.func == 9:  # NE    [sign extend imm to 64 bits & use 1 NOP]
                    self.rbi = (self.rai != self.imm)
                elif self.func == 10:  # LT    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    self.rbi = (self.rai < self.imm)
                elif self.func == 11:  # GE    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    self.rbi = (self.rai > self.imm)
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    self.rbi = (self.rai < self.imm)
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    self.rbi = (self.rai > self.imm)
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    self.rbi = min(self.rai, self.imm)
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    self.rbi = max(self.rai, self.imm)


            elif self.opcode == 36:  # same as above but with return Example: RETOP Rb = Ra, Imm12 // JR R31; OP Rb = Ra, Imm12 
                if self.func == 0:  # ADD   [sign extend imm to 64 bits]
                    rb = self.rai + self.imm
                elif self.func == 1:  # NADD  [sign extend imm to 64 bits]
                    rb = -self.rai + self.imm
                elif self.func == 2:  # AND   [sign extend imm to 64 bits]
                    rb = self.rai & self.imm
                elif self.func == 3:  # CAND  [sign extend imm to 64 bits]
                    rb = ~self.rai & self.imm
                elif self.func == 4:  # OR    [sign extend imm to 64 bits & use 1 NOP]
                    rb = self.rai | self.imm
                elif self.func == 5:  # COR   [sign extend imm to 64 bits & use 1 NOP]
                    rb = ~self.rai | self.imm
                elif self.func == 6:  # XOR   [sign extend imm to 64 bits & use 1 NOP]
                    rb = self.rai ^ self.imm
                elif self.func == 7:  # SET   [sign extend imm to 64 bits & use 1 NOP]
                    rb = self.imm
                elif self.func == 8:  # EQ    [sign extend imm to 64 bits & use 1 NOP]
                    rb = (self.rai == self.imm)
                elif self.func == 9:  # NE    [sign extend imm to 64 bits & use 1 NOP]
                    rb = (self.rai != self.imm)
                elif self.func == 10:  # LT    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rb = (self.rai < self.imm)
                elif self.func == 11:  # GE    [sign extend imm to 64 bits & use 1 NOP]  [signed   comparison]?
                    rb = (self.rai > self.imm)
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rb = (self.rai < self.imm)
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]?
                    rb = (self.rai > self.imm)
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    rb = min(self.rai, self.imm)
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    rb = max(self.rai, self.imm)


            # function for Creating unsigned number
            def unsign(value):
                if value >= 0: return value
                return value + (value << 64)


            # some needed conversions:
            sign_extended_64_imm = sign_extend(self.imm, 64)
            unsigned_rai = unsign(sim.regfile.get(self.rai))
            unsigned_imm = unsign(self.imm)
            unsigned_extended_64_imm = unsign(sign_extended_64_imm)

            # for self.opcode 32 - 35
            if self.opcode in {32, 33, 34,
                          45}:  # Rb is the destination here, also: [sign extend imm to 64 bits], NOP is not implemented
                if self.func == 0:  # ADD
                    #  rbi = rai + imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) + sign_extended_64_imm)
                elif self.func == 1:  # NADD  
                    #  rbi = -rai + imm
                    sim.regfile.set(self.rbi, -sim.regfile.get(self.rai) + sign_extended_64_imm)
                elif self.func == 2:  # AND   
                    #  rbi = rai & imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) & sign_extended_64_imm)
                elif self.func == 3:  # CAND  
                    #  rbi = ~rai & imm
                    sim.regfile.set(self.rbi, ~sim.regfile.get(self.rai) & sign_extended_64_imm)
                elif self.func == 4:  # OR   
                    #    rbi = rai | imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) | sign_extended_64_imm)
                elif self.func == 5:  # COR   
                    #    rbi = ~rai | imm
                    sim.regfile.set(self.rbi, ~sim.regfile.get(self.rai) | sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 6:  # XOR   
                    #   rbi = rai ^ imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) ^ sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 7:  # SET   
                    #   rbi = imm
                    sim.regfile.set(self.rbi, sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 8:  # EQ   
                    #    rbi = (rai == imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) == sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 9:  # NE    
                    #  rbi = (rai != imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) != sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 10:  # LT   
                    # rbi = (rai < imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) < sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 11:  # GE    
                    #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) > sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                    #  rbi = (rai < imm)
                    sim.regfile.set(self.rbi, (unsigned_rai < unsigned_extended_64_imm))  # [use 2 NOP]
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                    #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi, (unsigned_rai > unsigned_extended_64_imm))
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    #  rbi = min(rai, imm)
                    sim.regfile.set(self.rbi, min(sim.regfile.get(self.rai), sign_extended_64_imm))
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    #   rbi = max(rai, imm)
                    sim.regfile.set(self.rbi, max(sim.regfile.get(self.rai), sign_extended_64_imm))

                    # in this next self.opcode(36): RETURN/Jumping is not done yet
            elif self.opcode == 36:  # same as above but with return Example: RETOP Rb = Ra, Imm12 // JR R31; OP Rb = Ra, Imm12
                sim.regfile[31] = sim.pc
                if self.offset is not None:
                    print("Jumping with offset={}".format(self.offset))
                    sim.pc += self.offset
                else:
                    print("WARNING: return instruction doesn't have offset: {}".format(self))

                if self.func == 0:  # ADD
                    #  rbi = rai + imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) + sign_extended_64_imm)
                elif self.func == 1:  # NADD
                    #  rbi = -rai + imm
                    sim.regfile.set(self.rbi, -sim.regfile.get(self.rai) + sign_extended_64_imm)
                elif self.func == 2:  # AND
                    #  rbi = rai & imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) & sign_extended_64_imm)
                elif self.func == 3:  # CAND
                    #  rbi = ~rai & imm
                    sim.regfile.set(self.rbi, ~sim.regfile.get(self.rai) & sign_extended_64_imm)
                elif self.func == 4:  # OR
                    #    rbi = rai | imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) | sign_extended_64_imm)
                elif self.func == 5:  # COR
                    #    rbi = ~rai | imm
                    sim.regfile.set(self.rbi, ~sim.regfile.get(self.rai) | sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 6:  # XOR
                    #   rbi = rai ^ imm
                    sim.regfile.set(self.rbi, sim.regfile.get(self.rai) ^ sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 7:  # SET
                    #   rbi = imm
                    sim.regfile.set(self.rbi, sign_extended_64_imm)  # [use 1 NOP]
                elif self.func == 8:  # EQ
                    #    rbi = (rai == imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) == sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 9:  # NE
                    #  rbi = (rai != imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) != sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 10:  # LT
                    # rbi = (rai < imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) < sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 11:  # GE
                    #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) > sign_extended_64_imm))  # [use 1 NOP]
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                    #  rbi = (rai < imm)
                    sim.regfile.set(self.rbi, (unsigned_rai < unsigned_extended_64_imm))  # [use 2 NOP]
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                    #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi, (unsigned_rai > unsigned_extended_64_imm))
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                    #  rbi = min(rai, imm)
                    sim.regfile.set(self.rbi, min(sim.regfile.get(self.rai), sign_extended_64_imm))
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                    #   rbi = max(rai, imm)
                    sim.regfile.set(self.rbi, max(sim.regfile.get(self.rai), sign_extended_64_imm))


            # for self.Opcode 37 SHIFT
            elif self.opcode == 37:
                if self.func == 0:  # SHLR
                    #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, ((sim.regfile.get(self.rai) << self.imm_L) >> self.imm_R))
                elif self.func == 1:  # SHLR
                    #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, ((sim.regfile.get(self.rai) << self.imm_L) >> self.imm_R))
                elif self.func == 2:  # SALR
                    #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, (sign_extend(sim.regfile.get(self.rai) << self.imm_L) >> self.imm_R))
                elif self.func == 3:  # ROR  [ not sure about how to rotate bitwise ]
                    pass  # do
                elif self.func == 8:  # MUL   [signed]
                    sim.regfile.set(self.rdi, sim.regfile.get(self.rai) * sim.regfile.get(self.rbi))
                elif self.func == 12:  # DIV  [signed]
                    sim.regfile.set(self.rdi, sim.regfile.get(self.rai) // sim.regfile.get(self.rbi))
                elif self.func == 13:  # MOD  [signed]
                    sim.regfile.set(self.rdi, sim.regfile.get(self.rai) % sim.regfile.get(self.rbi))
                elif self.func == 14:  # DIVU [unsigned]
                    sim.regfile.set(self.rdi, unsign(sim.regfile.get(self.rai)) // unsign(sim.regfile.get(self.rbi)))
                elif self.func == 15:  # MODU [usigned]
                    sim.regfile.set(self.rdi, unsign(sim.regfile.get(self.rai)) % unsign(sim.regfile.get(self.rbi)))


            # for self.opcode 40
            elif self.opcode == 40:
                if self.x == 0:
                    if self.func == 0:  # ADD
                        #    rd = rai + rbi
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) + sim.regfile.get(self.rbi))
                    elif self.func == 1:  # NADD
                        #    rd = -rai + rbi
                        sim.regfile.set(self.rdi, -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi))
                    elif self.func == 2:  # AND
                        #    rd = rai & rbi
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) & sim.regfile.get(self.rbi))
                    elif self.func == 3:  # CAND
                        #     rd = ~rai & rbi
                        sim.regfile.set(self.rdi, ~sim.regfile.get(self.rai) & sim.regfile.get(self.rbi))
                    elif self.func == 4:  # OR
                        #  rd = rai | rbi
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) | sim.regfile.get(self.rbi))
                    elif self.func == 5:  # COR
                        #   rd = ~rai | rbi
                        sim.regfile.set(self.rdi, ~sim.regfile.get(self.rai) | sim.regfile.get(self.rbi))
                    elif self.func == 6:  # XOR
                        #   rd = rai ^ rbi
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi))
                    elif self.func == 7:  # XNOR
                        #   rd = ~rai ^ rbi
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi))
                    elif self.func == 8:  # EQ
                        #   rd = (rai == rbi)
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) == sim.regfile.get(self.rbi)))
                    elif self.func == 9:  # NE
                        #  rd = (rai != rbi)
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) != sim.regfile.get(self.rbi)))
                    elif self.func == 10:  # LT  [signed]
                        #  rd = (rai < rbi)
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) < sim.regfile.get(self.rbi)))
                    elif self.func == 11:  # GT  [signed]
                        #  rd = (rai > rbi)
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) > sim.regfile.get(self.rbi)))
                    elif self.func == 12:  # LTU [unsigned]
                        #  rd = (rai < rbi)
                        sim.regfile.set(self.rdi,
                                        (unsign(sim.regfile.get(self.rai)) < unsign(sim.regfile.get(self.rbi))))
                    elif self.func == 13:  # GTU [unsigned]
                        #  rd = (rai > rbi)
                        sim.regfile.set(self.rdi,
                                        (unsign(sim.regfile.get(self.rai)) > unsign(sim.regfile.get(self.rbi))))
                    elif self.func == 14:  # MIN
                        #    rd = min(rai, rbi)
                        sim.regfile.set(self.rdi, (min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi))))
                    elif self.func == 15:  # MAX
                        #    rd = max(rai, rbi)
                        sim.regfile.set(self.rdi, (min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi))))
                elif self.x == 2:
                    if self.func == 0:  # SHL
                        #    rd = (rbi << rai)
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) << sim.regfile.get(self.rbi))
                    elif self.func == 1:  # SHR
                        #   rd = (rbi >> rai)
                        sim.regfile.set(self.rdi, sim.regfile.get(self.rai) >> sim.regfile.get(self.rbi))
                    elif self.func == 2:  # SAR [ Shift to the right arithmetic, meaning: SIGNED extend after shifting]
                        #   rd = (rbi << rai)
                        sim.regfile.set(self.rdi, sign_extend(sim.regfile.get(self.rai) << sim.regfile.get(self.rbi)))
                    elif self.func == 3:  # ROR [ not sure how to rotate bitwise ]
                        pass  # do
                    elif self.func == 8:  # MUL [signed]
                        #  rd = rai * rbi
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) * sim.regfile.get(self.rbi)))
                    elif self.func == 12:  # DIV [signed]
                        # rd = rai // rbi
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) // sim.regfile.get(self.rbi)))
                    elif self.func == 13:  # MOD [signed]
                        #  rd = rai % rbi
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) % sim.regfile.get(self.rbi)))
                    elif self.func == 14:  # DIVU [unsigned]
                        #  rd = rai // rbi
                        sim.regfile.set(self.rdi,
                                        (unsign(sim.regfile.get(self.rai)) // unsign(sim.regfile.get(self.rbi))))
                    elif self.func == 15:  # MODU [unsigned]
                        #  rd = rai % rbi
                        sim.regfile.set(self.rdi,
                                        (unsign(sim.regfile.get(self.rai)) % unsign(sim.regfile.get(self.rbi))))
                elif self.x == 3:  # ADDS  Rd = Ra + Rb<<n
                    # rd = rai + (rbi << self.n)
                    sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) + (sim.regfile.get(self.rbi) << self.n)))
                elif self.x == 4:  # NADDS Rd = -Ra + Rb<<n
                    #  rd = -rai + (rbi << self.n)
                    sim.regfile.set(self.rdi, (-sim.regfile.get(self.rai) + (sim.regfile.get(self.rbi) << self.n)))

        elif self.opcode in Instruction.sections[5]:
            if self.x == 0:
                if self.func == 0:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci))
                elif self.func == 1:
                    sim.regfile.set(self.rdi,
                                    -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci))
                elif self.func == 2:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) & sim.regfile.get(self.rbi) & sim.regfile.get(self.rci))
                elif self.func == 3:
                    sim.regfile.set(self.rdi,
                                    ~sim.regfile.get(self.rai) & sim.regfile.get(self.rbi) & sim.regfile.get(self.rci))
                elif self.func == 4:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) | sim.regfile.get(self.rbi) | sim.regfile.get(self.rci))
                elif self.func == 5:
                    sim.regfile.set(self.rdi,
                                    ~sim.regfile.get(self.rai) | sim.regfile.get(self.rbi) | sim.regfile.get(self.rci))
                elif self.func == 6:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi) ^ sim.regfile.get(self.rci))
                elif self.func == 7:
                    sim.regfile.set(self.rdi,
                                    ~sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi) ^ sim.regfile.get(self.rci))
            elif self.x == 1:
                if self.func == 0:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) == sim.regfile.get(
                                        self.rci))
                elif self.func == 1:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) != sim.regfile.get(
                                        self.rci))
                elif self.func == 2:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))
                elif self.func == 3:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) > sim.regfile.get(self.rci))
                elif self.func == 4:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))
                elif self.func == 5:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) and sim.regfile.get(self.rbi) > sim.regfile.get(self.rci))
                elif self.func == 6:
                    sim.regfile.set(self.rdi, min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi),
                                                  sim.regfile.get(self.rci)))
                elif self.func == 7:
                    sim.regfile.set(self.rdi, max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi),
                                                  sim.regfile.get(self.rci)))
                elif self.func == 8:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 9:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 10:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 11:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 12:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 13:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) or sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))
                elif self.func == 14:
                    sim.regfile.set(self.rdi, min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi),
                                                  sim.regfile.get(self.rci)))
                elif self.func == 15:
                    sim.regfile.set(self.rdi, max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi),
                                                  sim.regfile.get(self.rci)))
                #Due to the logical operations rdi may have a boolean (True/False) ---> Must set it to (1/0)
                if sim.regfile.get(self.rdi) == True:
                    sim.regfile.set(self.rdi,1)
                elif sim.regfile.get(self.rdi) == False:
                    sim.regfile.set(self.rdi,0)
                
            elif self.x == 2:
                if self.func == 0:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rbi) if sim.regfile.get(self.rai) != 0 else sim.regfile.get(
                                        self.rdi))
                elif self.func == 1:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rbi) if sim.regfile.get(self.rai) < 0 else sim.regfile.get(
                                        self.rdi))
                elif self.func == 2:
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rbi) if sim.regfile.get(self.rai) > 0 else sim.regfile.get(
                                        self.rdi))
                elif self.func == 4:  # 3 is skipped according to doc
                    sim.regfile.set(self.rdi,
                                    sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci))
                elif self.func == 5:
                    sim.regfile.set(self.rdi,
                                    -sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci))
        elif self.opcode in Instruction.sections[6]:
            # for self.opcode 42 FPU1
            if self.opcode == 42:
                if self.p == 0:  # SINGLE PERCISION
                    if self.func == 0:  # ABS
                        sim.regfile.set(self.rdi, abs(sim.regfile.get(self.rai)))
                    elif self.func == 1:  # NEG
                        sim.regfile.set(self.rdi, ~(sim.regfile.get(self.rai)))
                    elif self.func == 2:  # SQRT
                        sim.regfile.set(self.rdi, math.sqrt(sim.regfile.get(self.rai)))
                    elif self.func == 4:  # CVTSD
                        pass  # do   # convert to single percision
                    elif self.func == 5:  # CVTSI
                        pass  # do
                    elif self.func == 6:  # CVTIS
                        pass  # do
                    elif self.func == 7:  # RINT
                        pass
                elif self.p == 1:  # DOUBLE PERCISION
                    if self.func == 0:  # ABS
                        sim.regfile.set(self.rdi, abs(sim.regfile.get(self.rai)))
                    elif self.func == 1:  # NEG
                        sim.regfile.set(self.rdi, ~(sim.regfile.get(self.rai)))
                    elif self.func == 2:  # SQRT
                        sim.regfile.set(self.rdi, math.sqrt(sim.regfile.get(self.rai)))
                    elif self.func == 4:  # CVTSD
                        pass  # do   # convert to single percision
                    elif self.func == 5:  # CVTSI
                        pass  # do
                    elif self.func == 6:  # CVTIS
                        pass  # do
                    elif self.func == 7:  # RINT
                        pass  # do


            # for self.opcode 43 FPU2
            elif self.opcode == 43:
                if self.p == 0:  # SINGLE PERCISION
                    if self.func == 0:  # EQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) == sim.regfile.get(self.rbi)))
                    elif self.func == 1:  # NE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) != sim.regfile.get(self.rbi)))
                    elif self.func == 2:  # LT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) < sim.regfile.get(self.rbi)))
                    elif self.func == 3:  # GE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) > sim.regfile.get(self.rbi)))
                    elif self.func == 4:  # INF
                        pass  # do
                    elif self.func == 5:  # NAN
                        pass  # do
                    elif self.func == 8:  # ADD
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) + sim.regfile.get(self.rbi)))
                    elif self.func == 9:  # NADD
                        sim.regfile.set(self.rdi, (-sim.regfile.get(self.rai) + sim.regfile.get(self.rbi)))
                    elif self.func == 10:  # MUL
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) * sim.regfile.get(self.rbi)))
                    elif self.func == 11:  # DIV
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) / sim.regfile.get(self.rbi)))
                    elif self.func == 12:  # MIN
                        sim.regfile.set(self.rdi, min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)))
                    elif self.func == 13:  # MAX
                        sim.regfile.set(self.rdi, max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)))
                elif self.p == 1:  # DOUBLE PERCISION
                    if self.func == 0:  # EQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) == sim.regfile.get(self.rbi)))
                    elif self.func == 1:  # NE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) != sim.regfile.get(self.rbi)))
                    elif self.func == 2:  # LT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) < sim.regfile.get(self.rbi)))
                    elif self.func == 3:  # GE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) > sim.regfile.get(self.rbi)))
                    elif self.func == 4:  # INF
                        pass  # do
                    elif self.func == 5:  # NAN
                        pass  # do
                    elif self.func == 8:  # ADD
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) + sim.regfile.get(self.rbi)))
                    elif self.func == 9:  # NADD
                        sim.regfile.set(self.rdi, (-sim.regfile.get(self.rai) + sim.regfile.get(self.rbi)))
                    elif self.func == 10:  # MUL
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) * sim.regfile.get(self.rbi)))
                    elif self.func == 11:  # DIV
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) / sim.regfile.get(self.rbi)))
                    elif self.func == 12:  # MIN
                        sim.regfile.set(self.rdi, min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)))
                    elif self.func == 13:  # MAX
                        sim.regfile.set(self.rdi, max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)))

            # for self.opcode 44 FPU3
            elif self.opcode == 44:
                if self.p == 0:  # SINGLE PERCISION
                    if self.func == 0:  # ANDEQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))))
                    elif self.func == 1:  # ANDNE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) != sim.regfile.get(self.rci))))
                    elif self.func == 2:  # ANDLT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))))
                    elif self.func == 3:  # ANDGE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci))))
                    elif self.func == 4:  # OREQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))))
                    elif self.func == 5:  # ORNE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) != sim.regfile.get(self.rci))))
                    elif self.func == 6:  # ORLT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))))
                    elif self.func == 7:  # ORGE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci))))
                    elif self.func == 8:  # ADD
                        sim.regfile.set(self.rdi, (
                                sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 9:  # NADD
                        sim.regfile.set(self.rdi, (
                                -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 10:  # MADD
                        sim.regfile.set(self.rdi, (
                                sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 11:  # NMADD
                        sim.regfile.set(self.rdi, (
                                -sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 12:  # MIN
                        sim.regfile.set(self.rdi, (
                            min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi), sim.regfile.get(self.rci))))
                    elif self.func == 13:  # MAX
                        sim.regfile.set(self.rdi, (
                            max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi), sim.regfile.get(self.rci))))
                elif self.p == 1:  # DOUBLE PERCISION
                    if self.func == 0:  # ANDEQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))))
                    elif self.func == 1:  # ANDNE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) != sim.regfile.get(self.rci))))
                    elif self.func == 2:  # ANDLT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))))
                    elif self.func == 3:  # ANDGE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) and (
                                sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci))))
                    elif self.func == 4:  # OREQ
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) == sim.regfile.get(self.rci))))
                    elif self.func == 5:  # ORNE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) != sim.regfile.get(self.rci))))
                    elif self.func == 6:  # ORLT
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) < sim.regfile.get(self.rci))))
                    elif self.func == 7:  # ORGE
                        sim.regfile.set(self.rdi, (sim.regfile.get(self.rai) or (
                                sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci))))
                    elif self.func == 8:  # ADD
                        sim.regfile.set(self.rdi, (
                                sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 9:  # NADD
                        sim.regfile.set(self.rdi, (
                                -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 10:  # MADD
                        sim.regfile.set(self.rdi, (
                                sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 11:  # NMADD
                        sim.regfile.set(self.rdi, (
                                -sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci)))
                    elif self.func == 12:  # MIN
                        sim.regfile.set(self.rdi, (
                            min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi), sim.regfile.get(self.rci))))
                    elif self.func == 13:  # MAX
                        sim.regfile.set(self.rdi, (
                            max(sim.regfile.get(self.rai), sim.regfile.get(self.rbi), sim.regfile.get(self.rci))))


    def __asInt__(self) -> (int, int, int):
        pass
