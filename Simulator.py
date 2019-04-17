from Addressable import Instruction
from AssembledFile import AssembledFile


class Simulator:
    def __init__(self, assembledFile=None, gui=None):
        self.regfile = Simulator.Regfile("gp")
        self.mem = Simulator.Mem()
        self.pc = 0  # the Prorgam Counter
        self.assembledFile = assembledFile
        self.gui = gui
        Simulator.sim = self


    def init(self, assembledFile: AssembledFile):
        """ resets the simulator, preparing it for a new file """
        self.__init__(assembledFile)
        # reset memory and stuff


    def executeInstruction(self, instruction: Instruction):
        instruction.execute(self)


    def step(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")

        if self.pc >= len(self.assembledFile.directiveSegments.get('.text')):
            print("reached end of .text segment")
            return
        next_instruction = self.assembledFile.directiveSegments.get('.text')[self.pc]
        self.executeInstruction(next_instruction)
        print('step() Run instr: "{0}"'
              '\nRegFile: {1}'.format(str(next_instruction), str(self.regfile)))
        self.pc += 1

        self.redisplayReg()
        self.redisplayMem()


    def runAll(self):
        print("runAll()")
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")
        else:
            instructions = self.assembledFile.directiveSegments.get('.text', [])
            for instr in instructions:
                if self.pc < len(instructions):
                    self.executeInstruction(instr)
                    print('Running instr: "{0}"'
                          '\nRegFile: {1}'.format(str(instr), str(self.regfile)))
                    self.pc += 1

            self.redisplayReg()
            self.redisplayMem()


    def redisplayMem(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            # This is a naaive way it can be optimized, no time
            self.gui.openScrollPane("memPane")
            index = 0
            for x in self.mem.theBytes:
                name = str(index) + "c1"
                self.gui.setLabel(name, self.mem.theBytes[index])
                index += 1
                # self.gui.stopScrollPane()


    def redisplayReg(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            self.gui.setLabel("Registers",
                              "R0 = {0}"
                              "\nR1 = {1}"
                              "\nR2 = {2}"
                              "\nR3 = {3}"
                              "\nR4 = {4}"
                              "\nR5 = {5}"
                              "\nR6 = {6}"
                              "\nR7 = {7}"
                              "\nR8 = {8}"
                              "\nR9 = {9}"
                              "\nR10 = {10}".format(
                                  self.regfile.get(0),
                                  self.regfile.get(1),
                                  self.regfile.get(2),
                                  self.regfile.get(3),
                                  self.regfile.get(4),
                                  self.regfile.get(5),
                                  self.regfile.get(6),
                                  self.regfile.get(7),
                                  self.regfile.get(8),
                                  self.regfile.get(9),
                                  self.regfile.get(10))
                              )
            self.gui.setLabel("Registers1",
                              "R11 = {0}"
                              "\nR12 = {1}"
                              "\nR13 = {2}"
                              "\nR14 = {3}"
                              "\nR15 = {4}"
                              "\nR16 = {5}"
                              "\nR17 = {6}"
                              "\nR18 = {7}"
                              "\nR19 = {8}"
                              "\nR18 = {9}"
                              "\nR21 = {10}".format(
                                  self.regfile.get(11),
                                  self.regfile.get(12),
                                  self.regfile.get(13),
                                  self.regfile.get(14),
                                  self.regfile.get(15),
                                  self.regfile.get(16),
                                  self.regfile.get(17),
                                  self.regfile.get(18),
                                  self.regfile.get(19),
                                  self.regfile.get(20),
                                  self.regfile.get(21))
                              )
            self.gui.setLabel("Registers2",
                              "R22 = {0}"
                              "\nR23 = {1}"
                              "\nR24 = {2}"
                              "\nR25 = {3}"
                              "\nR26 = {4}"
                              "\nR27 = {5}"
                              "\nR28 = {6}"
                              "\nR29 = {7}"
                              "\nR30 = {8}"
                              "\nR31 = {9}".format(
                                  self.regfile.get(22),
                                  self.regfile.get(23),
                                  self.regfile.get(24),
                                  self.regfile.get(25),
                                  self.regfile.get(26),
                                  self.regfile.get(17),
                                  self.regfile.get(28),
                                  self.regfile.get(29),
                                  self.regfile.get(30),
                                  self.regfile.get(31))
                              )

            for i in range(len(self.mem.theBytes)):
                name = "{0}c1".format(str(i))
                self.gui.setLabel(name, self.mem.theBytes[i])

            # self.gui.stopScrollPane()

    class Regfile:
        # (width in bits)

        # format of the reg file: (value, name, representation)
        # representation will be one of: ('fp', 'int', 'hex', 'bin', 'dec')
        initializer = {
            "gp": (32, ['r{}'.format(i) for i in range(32)], ['int'] * 32),
            "e": (64, ['e{}'.format(i) for i in range(64)], ['int'] * 64),
            "c": (64, ['c{}'.format(i) for i in range(64)], ['int'] * 64),
            "fp": (64, ['f{}'.format(i) for i in range(64)], ['fp'] * 64)
        }


        def __init__(self, name: str):
            """ :param name: decides the type of __regs__ to make. either one of: "gp", "e", "c", "fp" """
            # if someString in initializer:

            length, names, representations = Simulator.Regfile.initializer.get(name)

            self.name = name  # the name of THIS regfile (gp, e, c, fp)

            self.names = names  # list of reg names ['r0', 'r1', 'r2'...]
            self.__regs__ = [0] * length
            self.representations = representations

            self.__regs__[1] = 1  # DEBUG: FIXME: just for testing
            print("__regs__:", self.__regs__)


        def __setitem__(self, key, value):
            self.set(key, value)


        def __getitem__(self, key):
            return self.get(key)


        def set(self, index, newVal, instruction: Instruction = None):
            if type(index) is str:  # this line allows for indexing by reg names (as strings)
                index = self.names.index(index)

            print("setting reg {}: {} -> {}".format(index, self.__regs__[index], newVal))
            self.__regs__[index] = newVal


        def get(self, regIndex: int):
            return self.__regs__[regIndex]


        def __str__(self):
            return "{} register file:\n\t{}".format(self.name, "\n\t".join(map(str, zip(self.names, self.__regs__))))

    class Mem:
        def __init__(self):
            self.theBytes = ["00000000"] * 32


        def write(self, address, byteElements):
            for b in byteElements:
                self.theBytes[address] = b
                address += 1


        def __str__(self):
            return "Memory:\n\t{}".format("\n\t".join(map(str, zip(range(len(self.theBytes)), self.theBytes))))
