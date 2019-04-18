from Addressable import Instruction
from AssembledFile import AssembledFile


def parseFloatStr(string):
    return 0  # TODO:


def parseDecStr(string):
    return int(string)


def parseHexStr(string):
    return int(string, 16)


def parseBinStr(string):
    return int(string, 2)


representationParsers = {
    'fp': parseFloatStr,
    'hex': parseHexStr,
    'bin': parseBinStr,
    'dec': parseDecStr,
}


class Simulator:
    def __init__(self, assembledFile=None, gui=None):
        self.regfile = Simulator.Regfile("gp")
        self.mem = Simulator.Mem()
        self.pc = 0  # the Prorgam Counter
        self.assembledFile = assembledFile
        self.gui = gui
        Simulator.sim = self
        self.updateMemFromGUI()
        print(self.regfile)


    def init(self, *args, **kwargs):
        """ resets the simulator, preparing it for a new file """
        self.__init__(*args, **kwargs)
        self.updateMemFromGUI()
        self.updateRegsFromGUI()
        # reset memory and stuff


    def executeInstruction(self, instruction: Instruction):
        instruction.execute(self)


    def step(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")

        if self.pc >= len(self.assembledFile.directiveSegments.get('.text')):
            print("reached end of .text segment")
            return

        self.updateMemFromGUI()

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
            self.updateMemFromGUI()
            instructions = self.assembledFile.directiveSegments.get('.text', [])
            for instr in instructions:
                if self.pc < len(instructions):
                    self.executeInstruction(instr)
                    print('Running instr: "{0}"'
                          '\nRegFile: {1}'.format(str(instr), str(self.regfile)))
                    self.pc += 1

            self.redisplayReg()
            self.redisplayMem()


    def updateMemFromGUI(self):
        if self.gui is None:
            print("WARNING: simulator trying to update regs from gui but no gui object")
            return
        self.gui.openScrollPane("regs")

        for i, name, value, rep in self.regfile.items():
            guistr = self.gui.getEntry(name)
            representationParsers.get(rep)(guistr)

        self.gui.stopScrollPane()


    def updateRegsFromGUI(self):
        # self.gui.openScrollPane("memPane")
        #
        # for i, name, value, rep in self.regfile.items():
        #     guistr = self.gui.getEntry(name, value)
        #     representationParsers.get(rep)(guistr)
        #
        # self.gui.stopScrollPane()
        pass


    def redisplayMem(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            # This is a naaive way it can be optimized, no time
            self.gui.openScrollPane("memPane")
            for index in range(len(self.mem.theBytes)):
                name = str(index) + "c1"
                self.gui.setLabel(name, self.mem.theBytes[index])
                # self.gui.stopScrollPane()


    def redisplayReg(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            self.gui.openScrollPane("regs")

            for i, name, value, rep in self.regfile.items():
                self.gui.setEntry(name, value)
            self.gui.stopScrollPane()

    class Regfile:
        # (width in bits)

        # format of the reg file: (value, name, representation)
        # representation will be one of: ('fp', 'int', 'hex', 'bin', 'dec')
        initializer = {
            "gp": (32, ['r{}'.format(i) for i in range(32)], ['dec'] * 32),
            "e": (64, ['e{}'.format(i) for i in range(64)], ['dec'] * 64),
            "c": (64, ['c{}'.format(i) for i in range(64)], ['dec'] * 64),
            "fp": (64, ['f{}'.format(i) for i in range(64)], ['fp'] * 64)
        }


        def __init__(self, name: str):
            """ :param name: decides the type of __regs__ to make. either one of: "gp", "e", "c", "fp" """
            # if someString in initializer:

            length, names, representations = Simulator.Regfile.initializer.get(name)

            self.name = name  # the name of THIS regfile (gp, e, c, fp)

            self.__names__ = names  # list of reg __names__ ['r0', 'r1', 'r2'...]
            self.__regs__ = [0] * length
            self.representationParsers = representations

            self.__regs__[1] = 1  # DEBUG: FIXME: just for testing


        def items(self, stringify=False):
            """
            returns a list containing the info for each register
            :return: (index, name: str, value: int, representation: str)
            """
            if not stringify:
                return zip(range(len(self.__names__)), self.__names__, self.__regs__, self.representationParsers)
            return zip(map(str, range(len(self.__names__))), self.__names__, map(str, self.__regs__),
                       self.representationParsers)


        def __setitem__(self, key, value):
            self.set(key, value)


        def __getitem__(self, key):
            return self.get(key)


        def set(self, index, newVal, instruction: Instruction = None):
            if type(index) is str:  # this line allows for indexing by reg __names__ (as strings)
                index = self.__names__.index(index)

            print("setting reg {}: {} -> {}".format(index, self.__regs__[index], newVal))
            self.__regs__[index] = newVal


        def get(self, regIndex: int):
            return self.__regs__[regIndex]


        def __str__(self):
            return "{} register file:\n\t{}".format(self.name,
                                                    "\n\t".join(map(str, zip(self.__names__, self.__regs__))))

    class Mem:
        def __init__(self):
            self.theBytes = ["00000000"] * 32


        def write(self, address, byteElements):
            for b in byteElements:
                self.theBytes[address] = b
                address += 1


        def __str__(self):
            return "Memory:\n\t{}".format("\n\t".join(map(str, zip(range(len(self.theBytes)), self.theBytes))))
