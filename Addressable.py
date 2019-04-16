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

        from Assembler import decodeInstruction
        decodeInstruction(self)


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
        from Assembler import decodeToHex
        return decodeToHex(self)


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
        elif opcode in Instruction.sections[4]:   # Remember the NOP thing with every ALUI that has big imm
            rai = self.ra                         # '?' means a part i don't know how to do
            rbi = self.rb  
            imm = self.imm

            # function for SIGN-EXTENDING
             def sign_extend(value, bits):
                    sign_bit = 1 << (bits - 1)
                    return (value & (sign_bit - 1)) - (value & sign_bit)
                
            # function for Creating unsigned number
             def unsign(value):
                    if value >= 0: return value
                    return value + (value << 64)
                
            # some needed conversions: 
            sign_extended_64_imm = sign_extend(self.imm, 64)
            unsigned_rai = unsign(sim.regfile.get(self.rai))
            unsigned_imm = unsign(self.imm)
            unsigned_extended_64_imm = unsign(sign_extended_64_imm)

            # for opcode 32 - 35
            if opcode in {32, 33, 34, 45}:  # Rb is the destination here, also: [sign extend imm to 64 bits], NOP is not implemented
                if self.func == 0:    # ADD   
                  #  rbi = rai + imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) + sign_extended_64_imm )
                elif self.func == 1:  # NADD  
                  #  rbi = -rai + imm
                    sim.regfile.set(self.rbi,  -sim.regfile.get(self.rai) + sign_extended_64_imm )
                elif self.func == 2:  # AND   
                  #  rbi = rai & imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) & sign_extended_64_imm )
                elif self.func == 3:  # CAND  
                  #  rbi = ~rai & imm
                    sim.regfile.set(self.rbi,  ~sim.regfile.get(self.rai) & sign_extended_64_imm )
                elif self.func == 4:  # OR   
                #    rbi = rai | imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) | sign_extended_64_imm )
                elif self.func == 5:  # COR   
                #    rbi = ~rai | imm
                    sim.regfile.set(self.rbi,  ~sim.regfile.get(self.rai) | sign_extended_64_imm ) # [use 1 NOP]
                elif self.func == 6:  # XOR   
                 #   rbi = rai ^ imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) ^ sign_extended_64_imm )  # [use 1 NOP]
                elif self.func == 7:  # SET   
                 #   rbi = imm
                    sim.regfile.set(self.rbi,  sign_extended_64_imm )  # [use 1 NOP]
                elif self.func == 8:  # EQ   
                #    rbi = (rai == imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) == sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 9:  # NE    
                  #  rbi = (rai != imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) != sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 10:  # LT   
                   # rbi = (rai < imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) < sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 11:  # GE    
                  #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) > sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                  #  rbi = (rai < imm)
                    sim.regfile.set(self.rbi,  (unsigned_rai < unsigned_extended_64_imm ) # [use 2 NOP]
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                  #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi,  (unsigned_rai > unsigned_extended_64_imm) )
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                  #  rbi = min(rai, imm)
                    sim.regfile.set(self.rbi,  min(sim.regfile.get(self.rai), sign_extended_64_imm) )
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                 #   rbi = max(rai, imm)
                    sim.regfile.set(self.rbi,  max(sim.regfile.get(self.rai), sign_extended_64_imm) )

                                    
                    # in this next opcode(36): RETURN/Jumping is not done yet
            elif opcode == 36:  # same as above but with return Example: RETOP Rb = Ra, Imm12 // JR R31; OP Rb = Ra, Imm12 
                if self.func == 0:    # ADD   
                  #  rbi = rai + imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) + sign_extended_64_imm )
                elif self.func == 1:  # NADD  
                  #  rbi = -rai + imm
                    sim.regfile.set(self.rbi,  -sim.regfile.get(self.rai) + sign_extended_64_imm )
                elif self.func == 2:  # AND   
                  #  rbi = rai & imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) & sign_extended_64_imm )
                elif self.func == 3:  # CAND  
                  #  rbi = ~rai & imm
                    sim.regfile.set(self.rbi,  ~sim.regfile.get(self.rai) & sign_extended_64_imm )
                elif self.func == 4:  # OR   
                #    rbi = rai | imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) | sign_extended_64_imm )
                elif self.func == 5:  # COR   
                #    rbi = ~rai | imm
                    sim.regfile.set(self.rbi,  ~sim.regfile.get(self.rai) | sign_extended_64_imm ) # [use 1 NOP]
                elif self.func == 6:  # XOR   
                 #   rbi = rai ^ imm
                    sim.regfile.set(self.rbi,  sim.regfile.get(self.rai) ^ sign_extended_64_imm )  # [use 1 NOP]
                elif self.func == 7:  # SET   
                 #   rbi = imm
                    sim.regfile.set(self.rbi,  sign_extended_64_imm )  # [use 1 NOP]
                elif self.func == 8:  # EQ   
                #    rbi = (rai == imm)
                    sim.regfile.set(self.rbi, (sim.regfile.get(self.rai) == sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 9:  # NE    
                  #  rbi = (rai != imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) != sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 10:  # LT   
                   # rbi = (rai < imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) < sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 11:  # GE    
                  #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi,  (sim.regfile.get(self.rai) > sign_extended_64_imm) ) # [use 1 NOP]
                elif self.func == 12:  # LTU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                  #  rbi = (rai < imm)
                    sim.regfile.set(self.rbi,  (unsigned_rai < unsigned_extended_64_imm ) # [use 2 NOP]
                elif self.func == 13:  # GEU   [sign extend imm to 64 bits & use 2 NOP]  [unsigned comparison]
                  #  rbi = (rai > imm)
                    sim.regfile.set(self.rbi,  (unsigned_rai > unsigned_extended_64_imm) )
                elif self.func == 14:  # MIN   [sign extend imm to 64 bits & use 2 NOP]
                  #  rbi = min(rai, imm)
                    sim.regfile.set(self.rbi,  min(sim.regfile.get(self.rai), sign_extended_64_imm) )
                elif self.func == 15:  # MAX   [sign extend imm to 64 bits & use 2 NOP]
                 #   rbi = max(rai, imm)
                    sim.regfile.set(self.rbi,  max(sim.regfile.get(self.rai), sign_extended_64_imm) )


            # for Opcode 37 SHIFT
            elif opcode == 37:
                if self.func == 0:  # SHLR
                  #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, ( (sim.regfile.get(self.rai)<< self.imm_L) >> self.imm_R )
                elif self.func == 1:  # SHLR
                  #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, ( (sim.regfile.get(self.rai)<< self.imm_L) >> self.imm_R )
                elif self.func == 2:  # SALR
                  #  rbi = ((rai << self.imm_L) >> self.imm_R)
                    sim.regfile.set(self.rdi, ( sign_extend(sim.regfile.get(self.rai)<< self.imm_L) >> self.imm_R )
                elif self.func == 3:  # ROR  [ not sure about how to rotate bitwise ]
                    pass  # do
                elif self.func == 8:  # MUL   [signed]
                    sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) )
                elif self.func == 12:  # DIV  [signed]
                    sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) // sim.regfile.get(self.rbi) )
                elif self.func == 13:  # MOD  [signed]
                    sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) % sim.regfile.get(self.rbi) )
                elif self.func == 14:  # DIVU [unsigned]
                    sim.regfile.set(self.rdi,  unsign(sim.regfile.get(self.rai)) // unsign(sim.regfile.get(self.rbi)) )
                elif self.func == 15:  # MODU [usigned]
                    sim.regfile.set(self.rdi,  unsign(sim.regfile.get(self.rai)) % unsign(sim.regfile.get(self.rbi)) )


            # for opcode 40
            elif opcode == 40:
                if self.x == 0:
                    if self.func == 0:    # ADD
                   #    rd = rai + rbi
                        sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) )
                    elif self.func == 1:  # NADD
                   #    rd = -rai + rbi
                        sim.regfile.set(self.rdi,  -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) )
                    elif self.func == 2:  # AND
                   #    rd = rai & rbi
                        sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) & sim.regfile.get(self.rbi) )
                    elif self.func == 3:  # CAND
                  #     rd = ~rai & rbi
                        sim.regfile.set(self.rdi,  ~sim.regfile.get(self.rai) & sim.regfile.get(self.rbi) ) 
                    elif self.func == 4:  # OR
                      #  rd = rai | rbi
                         sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) | sim.regfile.get(self.rbi) )
                    elif self.func == 5:  # COR
                     #   rd = ~rai | rbi
                        sim.regfile.set(self.rdi,  ~sim.regfile.get(self.rai) | sim.regfile.get(self.rbi) )
                    elif self.func == 6:  # XOR
                     #   rd = rai ^ rbi
                         sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi) )
                    elif self.func == 7:  # XNOR
                     #   rd = ~rai ^ rbi
                         sim.regfile.set(self.rdi,  sim.regfile.get(self.rai) ^ sim.regfile.get(self.rbi) )
                    elif self.func == 8:  # EQ
                     #   rd = (rai == rbi)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) == sim.regfile.get(self.rbi) )
                    elif self.func == 9:  # NE
                      #  rd = (rai != rbi)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) != sim.regfile.get(self.rbi) )
                    elif self.func == 10:  # LT  [signed]
                      #  rd = (rai < rbi)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) < sim.regfile.get(self.rbi) )
                    elif self.func == 11:  # GT  [signed]
                      #  rd = (rai > rbi)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) > sim.regfile.get(self.rbi) )
                    elif self.func == 12:  # LTU [unsigned]
                     #  rd = (rai < rbi)
                         sim.regfile.set(self.rdi, ( unsign(sim.regfile.get(self.rai)) < unsign(sim.regfile.get(self.rbi)) )
                    elif self.func == 13:  # GTU [unsigned]
                     #  rd = (rai > rbi)
                         sim.regfile.set(self.rdi, ( unsign(sim.regfile.get(self.rai)) > unsign(sim.regfile.get(self.rbi)) )
                    elif self.func == 14:  # MIN
                    #    rd = min(rai, rbi)
                         sim.regfile.set(self.rdi, ( min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)) )                    
                    elif self.func == 15:  # MAX
                    #    rd = max(rai, rbi)           
                         sim.regfile.set(self.rdi, ( min(sim.regfile.get(self.rai), sim.regfile.get(self.rbi)) )
                elif self.x == 2:
                    if self.func == 0:  # SHL
                    #    rd = (rbi << rai)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) << sim.regfile.get(self.rbi)) )
                    elif self.func == 1:  # SHR
                    #   rd = (rbi >> rai)
                        sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) >> sim.regfile.get(self.rbi)) )
                    elif self.func == 2:  # SAR [ Shift to the right arithmetic, meaning: SIGNED extend after shifting]
                     #   rd = (rbi << rai)
                         sim.regfile.set(self.rdi, sign_extend(sim.regfile.get(self.rai) << sim.regfile.get(self.rbi)) )
                    elif self.func == 3:  # ROR [ not sure how to rotate bitwise ]
                        pass  # do
                    elif self.func == 8:  # MUL [signed]
                      #  rd = rai * rbi
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) * sim.regfile.get(self.rbi)) )
                    elif self.func == 12:  # DIV [signed]
                      # rd = rai // rbi
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) // sim.regfile.get(self.rbi)) )
                    elif self.func == 13:  # MOD [signed]
                      #  rd = rai % rbi
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) % sim.regfile.get(self.rbi)) )
                    elif self.func == 14:  # DIVU [unsigned]
                      #  rd = rai // rbi
                         sim.regfile.set(self.rdi, ( unsign(sim.regfile.get(self.rai)) // unsign(sim.regfile.get(self.rbi))) )
                    elif self.func == 15:  # MODU [unsigned]
                      #  rd = rai % rbi
                         sim.regfile.set(self.rdi, ( unsign(sim.regfile.get(self.rai)) % unsign(sim.regfile.get(self.rbi))) )
                elif self.x == 3:  # ADDS  Rd = Ra + Rb<<n
                   # rd = rai + (rbi << self.n)
                         sim.regfile.set(self.rdi, ( sim.regfile.get(self.rai) + (sim.regfile.get(self.rbi) << self.n )))
                elif self.x == 4:  # NADDS Rd = -Ra + Rb<<n
                   #  rd = -rai + (rbi << self.n)
                         sim.regfile.set(self.rdi, ( -sim.regfile.get(self.rai) + (sim.regfile.get(self.rbi) << self.n)))


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
            rai = self.ra                        
            rbi = self.rb  
            imm = self.imm


            # for opcode 42 FPU1
            if opcode == 42:  
                   if self.p == 0:                          # SINGLE PERCISION
                        if self.func == 0:   # ABS
                            sim.regfile.set( self.rdi, abs(sim.regfile.get(self.rai)) )
                        elif self.func == 1: # NEG
                            sim.regfile.set( self.rdi, ~(sim.regfile.get(self.rai)) )
                        elif self.func == 2: # SQRT
                            sim.regfile.set( self.rdi, sqrt(sim.regfile.get(self.rai)) )
                        elif self.func == 4: # CVTSD
                            pass # do   # convert to single percision 
                        elif self.func == 5: # CVTSI
                            pass  # do    
                        elif self.func == 6: # CVTIS
                            pass  # do
                        elif self.func == 7: # RINT
                   elif self.p == 1:                      # DOUBLE PERCISION
                        if self.func == 0:   # ABS
                            sim.regfile.set( self.rdi, abs(sim.regfile.get(self.rai)) )
                        elif self.func == 1: # NEG
                            sim.regfile.set( self.rdi, ~(sim.regfile.get(self.rai)) )
                        elif self.func == 2: # SQRT
                            sim.regfile.set( self.rdi, sqrt(sim.regfile.get(self.rai)) )
                        elif self.func == 4: # CVTSD
                            pass # do   # convert to single percision 
                        elif self.func == 5: # CVTSI
                            pass  # do    
                        elif self.func == 6: # CVTIS
                            pass  # do
                        elif self.func == 7: # RINT
                            pass  # do
                                         
                                         
            # for opcode 43 FPU2                            
            elif opcode == 43:  
                   if self.p == 0:                     # SINGLE PERCISION
                        if self.func == 0:   # EQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) == sim.regfile.get(self.rbi) ) )
                        elif self.func == 1: # NE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) != sim.regfile.get(self.rbi) ) )
                        elif self.func == 2: # LT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) < sim.regfile.get(self.rbi) ) )
                        elif self.func == 3: # GE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) > sim.regfile.get(self.rbi) ) )
                        elif self.func == 4: # INF
                            pass  # do    
                        elif self.func == 5: # NAN
                            pass  # do
                        elif self.func == 8: # ADD
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) ) )
                        elif self.func == 9: # NADD
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) ) )
                        elif self.func == 10: # MUL
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) ) )
                        elif self.func == 11: # DIV
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) / sim.regfile.get(self.rbi) ) )
                        elif self.func == 12: # MIN  
                            sim.regfile.set( self.rdi, min( sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) ) )
                        elif self.func == 13: # MAX  
                            sim.regfile.set( self.rdi, max( sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) ) )
                   elif self.p == 1:                  # DOUBLE PERCISION
                        if self.func == 0:   # EQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) == sim.regfile.get(self.rbi) ) )
                        elif self.func == 1: # NE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) != sim.regfile.get(self.rbi) ) )
                        elif self.func == 2: # LT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) < sim.regfile.get(self.rbi) ) )
                        elif self.func == 3: # GE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) > sim.regfile.get(self.rbi) ) )
                        elif self.func == 4: # INF
                            pass  # do    
                        elif self.func == 5: # NAN
                            pass  # do
                        elif self.func == 8: # ADD
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) ) )
                        elif self.func == 9: # NADD
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) ) )
                        elif self.func == 10: # MUL
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) ) )
                        elif self.func == 11: # DIV
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) / sim.regfile.get(self.rbi) ) )
                        elif self.func == 12: # MIN  
                            sim.regfile.set( self.rdi, min( sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) ) )
                        elif self.func == 13: # MAX  
                            sim.regfile.set( self.rdi, max( sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) ) )

                                         
                                         
                                         
            # for opcode 44 FPU3                            
            elif opcode == 44:  
                   if self.p == 0:                      # SINGLE PERCISION
                        if self.func == 0:   # ANDEQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) == sim.regfile.get(self.rci)) ) )
                        elif self.func == 1: # ANDNE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) != sim.regfile.get(self.rci)) ) )
                        elif self.func == 2: # ANDLT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) < sim.regfile.get(self.rci)) ) )
                        elif self.func == 3: # ANDGE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci)) ) )
                        elif self.func == 4: # OREQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) == sim.regfile.get(self.rci)) ) )
                        elif self.func == 5: # ORNE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) != sim.regfile.get(self.rci)) ) )
                        elif self.func == 6: # ORLT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) < sim.regfile.get(self.rci)) ) )
                        elif self.func == 7: # ORGE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci)) ) )
                        elif self.func == 8: # ADD
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 9: # NADD
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 10: # MADD  
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 11: # NMADD  
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 12: # MIN
                            sim.regfile.set( self.rdi, ( min(sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) , sim.regfile.get(self.rci)) )
                        elif self.func == 13: # MAX  
                            sim.regfile.set( self.rdi, ( max(sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) , sim.regfile.get(self.rci)) )
                   elif self.p == 1:                     # DOUBLE PERCISION
                        if self.func == 0:   # ANDEQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) == sim.regfile.get(self.rci)) ) )
                        elif self.func == 1: # ANDNE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) != sim.regfile.get(self.rci)) ) )
                        elif self.func == 2: # ANDLT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) < sim.regfile.get(self.rci)) ) )
                        elif self.func == 3: # ANDGE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) and (sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci)) ) )
                        elif self.func == 4: # OREQ
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) == sim.regfile.get(self.rci)) ) )
                        elif self.func == 5: # ORNE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) != sim.regfile.get(self.rci)) ) )
                        elif self.func == 6: # ORLT
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) < sim.regfile.get(self.rci)) ) )
                        elif self.func == 7: # ORGE
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) or (sim.regfile.get(self.rbi) >= sim.regfile.get(self.rci)) ) )
                        elif self.func == 8: # ADD
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 9: # NADD
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) + sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 10: # MADD  
                            sim.regfile.set( self.rdi, ( sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 11: # NMADD  
                            sim.regfile.set( self.rdi, ( -sim.regfile.get(self.rai) * sim.regfile.get(self.rbi) + sim.regfile.get(self.rci) )
                        elif self.func == 12: # MIN
                            sim.regfile.set( self.rdi, ( min(sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) , sim.regfile.get(self.rci)) )
                        elif self.func == 13: # MAX  
                            sim.regfile.set( self.rdi, ( max(sim.regfile.get(self.rai) , sim.regfile.get(self.rbi) , sim.regfile.get(self.rci)) )
                                         
                                         
    def __asInt__(self) -> (int, int, int):
        pass
