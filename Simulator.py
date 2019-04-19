from Addressable import Instruction
from AssembledFile import AssembledFile

printContent = False

def parseFloatStr(string):
    return 0 if not string else 0 # TODO:
def parseDecStr(string):
    return 0 if not string else int(string)
def parseHexStr(string):
    return 0 if not string else int(string, 16)
def parseBinStr(string):
    return 0 if not string else int(string, 2)
def parseAsciiStr(string):
    return 0 if not string else 0 #TODO:

representationParsers = {
    'fp': parseFloatStr,
    'hex': parseHexStr,
    'bin': parseBinStr,
    'dec': parseDecStr,
    'ascii': parseAsciiStr,
}

import re
# assuming the input value is a signed decimal value (TODO: this should become bytes)
addressBits = 64
addressBytes = addressBits//8
representationFormatter = {
    # TODO: replace those '' with '0's, and make the entries in the gui wider
    'fp': lambda val: re.sub(r'\s', '', format(val, str(addressBits)+'b')), #TODO: format to floating point
    'hex': lambda val: re.sub(r'\s', '', format(val, str(addressBytes//2)+'x')),
    'bin': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'b')),
    'dec': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'d')),
    'ascii': lambda val: re.sub(r'\s', '', format(val, str(addressBytes//2)+'x')), #TODO: this is bs, just a place holder
}


class Simulator:

    reps = ['fp', 'hex', 'bin', 'dec', 'ascii']

    def __init__(self, assembledFile=None, gui=None):
        self.regfile = Simulator.Regfile("gp")
        self.mem = Simulator.Mem(size=32)
        self.pc = 0  # the Prorgam Counter
        self.assembledFile = assembledFile
        self.gui = gui
        Simulator.sim = self
        self.updateMemFromGUI()
        print(self.regfile)


    def init(self, *args, **kwargs):
        """ resets the simulator, preparing it for a new file """
        self.__init__(*args, **kwargs)
        if self.gui:
            self.updateMemFromGUI()
            self.updateRegsFromGUI()
        # reset memory and stuff

    def log(self, *args):
        if self.gui:
            self.gui.getTextArea('console', *args)
        else:
            print('CONSOLE:', *args)

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

        print('step() Run instr: "{0}"'.format(str(next_instruction.lineStr)))
        if printContent:
            print('RegFile: {1}'.format(str(self.regfile)))
        
        self.pc += 1

        self.redisplayReg()
        self.redisplayMem()


    def runAll(self):
        print("runAll()")
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")
        else:
            self.updateMemFromGUI()
            self.updateRegsFromGUI()

            instructions = self.assembledFile.directiveSegments.get('.text', [])
            for instr in instructions:
                if self.pc < len(instructions):
                    self.executeInstruction(instr)

                    if printContent:
                        print('Running instr: "{0}"'
                            '\nRegFile: {1}'.format(str(instr), str(self.regfile)))
                    self.pc += 1

            self.redisplayReg()
            self.redisplayMem()


    def updateRegsFromGUI(self):
        self.gui.openScrollPane("regs")
        for i, name, value, rep in self.regfile.items():
            guistr = self.gui.getEntry(name+"_entry")
            self.regfile[i] = representationParsers.get(rep)(guistr)
        self.gui.stopScrollPane()
        
        self.redisplayMem()


    def updateMemFromGUI(self):
        if self.gui is None:
            print("WARNING: simulator trying to update regs from gui but no gui object")
            return
        self.gui.openScrollPane("regs")

        # iterating over the names and getting the values
        for i, name, value, rep in self.mem.items():
            guistr = self.gui.getEntry(name+"_entry")
            self.mem[i] = representationParsers.get(rep)(guistr)

        self.gui.stopScrollPane()
        self.redisplayMem()


    def redisplayMem(self):
        if self.gui is None:
            # raise Exception("No gui object")
            if printContent:
                print("Mem content: {}".format(self.mem.theBytes))
            pass
        else: # if gui:
            self.gui.openScrollPane("memPane")

            for i, name, value, rep in self.mem.items():
                formatted = representationFormatter.get(rep)(value)
                self.gui.setEntry(name+"_entry", formatted)
                # self.gui.stopScrollPane()

    def redisplayReg(self):
        if self.gui is None:
            # raise Exception("No gui object")
            if printContent:
                print("Register content: {}".format(self.regfile))
            pass
        else:
            self.gui.openScrollPane("regs")

            for i, name, value, rep in self.regfile.items():
                formatted = representationFormatter.get(rep)(value) #TODO: use a formatter, have a dictionary just like the parser (but the opposite)
                self.gui.setEntry(name+"_entry", formatted)
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
            # self.representationParsers = representations
            self.__reps__ = representations
            # the representation, but as a number, translate to string using Simulator.reps
            self.__repIndexes__ = list(map(lambda idx: Simulator.reps.index(idx), self.__reps__))
            
            self.__regs__[1] = 1  # DEBUG: FIXME: just for testing


        def items(self, stringify=False):
            """
            returns a list containing the info for each register
            :return: (index, name: str, value: int, representation: str)
            """
            if not stringify:
                return zip(range(len(self.__names__)), self.__names__, self.__regs__, self.__reps__)
            return zip(map(str, range(len(self.__names__))), self.__names__, map(str, self.__regs__), self.__reps__)


        def __setitem__(self, key, value):
            self.set(key, value)


        def __getitem__(self, key):
            return self.get(key)


        def set(self, index, newVal, instruction: Instruction = None):
            if type(index) is str:  # this line allows for indexing by reg __names__ (as strings)
                index = self.__names__.index(index)

            # TODO: do something here to check the instruction and to auto-set the rep depending on the instruction
            print("reg {}: {} -> {}".format(self.__names__[index], self.__regs__[index], newVal))
            self.__regs__[index] = newVal


        def get(self, regIndex: int):
            return self.__regs__[regIndex]

        def cycleRep(self, regIndex):
            # increment the repIndex
            self.__repIndexes__[regIndex] = (self.__repIndexes__[regIndex]+1)%len(Simulator.reps)
            # update rep
            self.__reps__[regIndex] = Simulator.reps[self.__repIndexes__[regIndex]] # use the map
            return self.__reps__[regIndex]


        def __str__(self):
            return "{} register file:\n\t{}".format(self.name,
                                                    "\n\t".join(map(str, zip(self.__names__, self.__regs__))))


    class Mem:
        def __init__(self, size=2**64):
            self.theBytes = [0] * size
            self.__names__ = ['Mem{}'.format(i) for i in range(size)]
            self.__repIndexes__ = [0] * size # the representation, but as a number, translate to string using Simulator.reps
            self.__reps__ = list(map(lambda idx: Simulator.reps[idx], self.__repIndexes__))
            self.__current__ = 0


        def set(self, address, byteElements):
            for b in [byteElements]: # if multiple elements
                self.theBytes[address] = b
                address += 1

        def items(self):
            """
            the names are the same names used in the gui
            :returns the items (index, name:str, byte, rep)
            """
            return zip(range(len(self.theBytes)), self.__names__, self.theBytes, self.__reps__)

        def get(self, address, nbytes=1):
            return self.theBytes[address:address + nbytes]

        def cycleRep(self, regIndex):
            # increment the repIndex
            self.__repIndexes__[regIndex] = (self.__repIndexes__[regIndex]+1)%len(Simulator.reps)
            # update rep
            self.__reps__[regIndex] = Simulator.rep[self.__repIndexes__[regIndex]] # use the map
            return self.__reps__[regIndex]

        def __setitem__(self, key, value):
            self.set(key, value)


        def __getitem__(self, key):
            return self.get(key)

        def __length__(self):
            return len(self.theBytes)

        def __iter__(self):
            return self

        def next(self): # Python 3: def __next__(self)
            if self.__current__ > len(self.theBytes)-1:
                self.__current__ = 0
                raise StopIteration
            else:
                self.__current__ += 1
                return self.theBytes[self.__current__]

        def __str__(self):
            return "Memory:\n\t{}".format("\n\t".join(map(str, zip(range(len(self.theBytes)), self.theBytes))))
