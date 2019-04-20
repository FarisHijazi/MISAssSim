from Addressable import Instruction
from AssembledFile import AssembledFile
import struct
import ctypes

printContent = False

def parseFloatStr(string):
    return 0 if not string else float(string)  # TODO:

def parseDecStr(string):
    return 0 if not string else int(string)

def parseHexStr(string):
    return 0 if not string else int(string, 16)

def parseBinStr(string):
    return 0 if not string else int(string, 2)

def parseAsciiStr(string):
    return 0 if not string else ord(string)

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
    'fp': lambda val: re.sub(r'\s', '', format(val, str(addressBits)+'f')), #TODO: format to floating point
    'hex': lambda val: re.sub(r'\s', '', format(val, str(addressBytes//2)+'x')),
    'bin': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'b')),
    'dec': lambda val: re.sub(r'\s', '', format(val, str(addressBytes)+'d')),
    'ascii': lambda val: (chr(val)),
}


class Simulator:
    def __init__(self, assembledFile=None, gui=None):
        self.regfile = Storage(sim=self, name="gp")
        self.mem = Mem(sim=self, name="Mem", size=32)
        self.pc = 0  # the Prorgam Counter
        self.assembledFile = assembledFile
        self.gui = gui
        Simulator.sim = self

        self.regfile.updateFromGUI()
        self.mem.updateFromGUI()
        print(self.regfile)


    def init(self, *args, **kwargs):
        """ resets the simulator, preparing it for a new file """
        self.__init__(*args, **kwargs)
        if self.gui:
            self.regfile.updateFromGUI()
            self.mem.updateFromGUI()
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

        self.mem.updateFromGUI()
        self.regfile.updateFromGUI()

        next_instruction = self.assembledFile.directiveSegments.get('.text')[self.pc]
        self.executeInstruction(next_instruction)

        print('step() Run instr: "{0}"'.format(str(next_instruction.lineStr)))
        if printContent:
            print('RegFile: {1}'.format(str(self.regfile)))
        
        self.pc += 1

        self.regfile.redisplay()
        self.mem.redisplay()


    def runAll(self):
        print("runAll()")
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")
        else:
            self.regfile.updateFromGUI()
            self.mem.updateFromGUI()

            instructions = self.assembledFile.directiveSegments.get('.text', [])
            for instr in instructions:
                if self.pc < len(instructions):
                    self.executeInstruction(instr)

                    if printContent:
                        print('Running instr: "{0}"'
                            '\nRegFile: {1}'.format(str(instr), str(self.regfile)))
                    self.pc += 1

            self.regfile.redisplay()
            self.mem.redisplay()


class Storage:
    # format of the reg file: (value, name, representation)
    # representation will be one of: ('fp', 'int', 'hex', 'bin', 'dec')
    initializers = {
        "gp": (32, ['r{}'.format(i) for i in range(32)], ['dec']),
        "e": (64, ['e{}'.format(i) for i in range(64)], ['dec']),
        "c": (64, ['c{}'.format(i) for i in range(64)], ['dec']),
        "fp": (64, ['f{}'.format(i) for i in range(64)], ['fp']),
        "Mem": (64, ['Mem{}'.format(i) for i in range(64)], ['hex']),

    }

    reps = ['fp', 'hex', 'bin', 'dec', 'ascii']


    # (width in bits)
    def __init__(self, sim: Simulator, size: int = 32, name: str = None, initializer=None):
        # NOTE: name will be used as the title in appjar, must be unique
        self.name = name  # the name of THIS storage object (mem, gp, e, c, fp)

        init = Storage.initializers.get(name, None)

        if initializer is not None:
            init = initializer
        
        size, names, reps = init

        self.size = size
        self.__names__ = names
        self.__reps__ = reps * size

        self.sim = sim

        if not hasattr(self, '__names__'):
            self.__names__ = names  # list of __names__ ['r0', 'r1', 'r2'...]

        if not hasattr(self, '__values__'):
            self.__values__ = [0] * size

        # self.representationParsers = representations
        # the representation, but as a number, translate to string using Storage.reps
        self.__repIndexes__ = list(map(lambda idx: Storage.reps.index(idx), self.__reps__))
        self.__current__ = 0
        

    def items(self, stringify=False):
        """
        returns a list containing the info for each register
        :return: (index, name: str, value: int, representation: str)
        """
        if not stringify:
            return zip(range(len(self.__names__)), self.__names__, self.__values__, self.__reps__)
        return zip(map(str, range(len(self.__names__))), self.__names__, map(str, self.__values__), self.__reps__)


    def buildGUI(self):
        # NOTE: scrollPane must already be opened before calling this method
        # building memory gui
        greyToggle = False
        for i, name, value, rep in self.items():

            self.sim.gui.addButton(
                name, column=1, colspan=1,
                func=lambda btnName: self.cycleRep(self.__names__.index(btnName))
            )
            self.sim.gui.entry(name + "_entry", value=value, row=i, column=2, colspan=10)
            self.sim.gui.addLabel(name + "_rep", text=rep, row=i, column=3, colspan=1, selectable=False)

            if greyToggle:
                self.sim.gui.setEntryBg(name + "_entry", "grey")
                self.sim.gui.setButtonBg(name, "grey")
                self.sim.gui.setLabelBg(name + "_rep", "grey")
            greyToggle = not greyToggle
        self.sim.gui.stopScrollPane()
        self.redisplay()


    def updateFromGUI(self):
        if self.sim.gui is None:
            print("WARNING: simulator trying to update from gui but no gui object")
            return
        self.sim.gui.openScrollPane(self.name)

        # iterating over the names and getting the values
        for i, name, value, rep in self.items():
            guistr = self.sim.gui.getEntry(name + "_entry")
            self[i] = representationParsers.get(rep)(guistr)

        self.sim.gui.stopScrollPane()
        self.redisplay()

    
    def redisplay(self, index=-1):
        if self.sim.gui is None:
            # raise Exception("No gui object")
            if printContent:
                print("Content: {}".format(self))
            pass
        else:
            self.sim.gui.openScrollPane(self.name)

            for i, name, value, rep in self.items():
                if index == -1 or i == index:
                    formatted = representationFormatter.get(rep)(value)
                    self.sim.gui.setEntry(name + "_entry", formatted)
                    self.sim.gui.setLabel(name + "_rep", rep)
            self.sim.gui.stopScrollPane()


    def cycleRep(self, index):
        """
        :param index - index of the value
        """
        self.updateFromGUI()

        # increment the repIndex
        self.__repIndexes__[index] = (self.__repIndexes__[index] + 1) % len(Storage.reps)
        # update rep str
        self.__reps__[index] = Storage.reps[self.__repIndexes__[index]]  # map repr number to repr str

        self.redisplay(index)
        return self.__reps__[index]


    def set(self, index, newVal, instruction: Instruction = None):
        if type(index) is str:  # this line allows for indexing by reg __names__ (as strings)
            index = self.__names__.index(index)

        # TODO: do something here to check the instruction and to auto-set the rep depending on the instruction
        print("set {}: {} -> {}".format(self.__names__[index], self.__values__[index], newVal))
        self.__values__[index] = newVal
        self.redisplay(index)


    def get(self, index: int):
        if type(index) is str:  # this line allows for indexing by reg __names__ (as strings)
            index = self.__names__.index(index)
        return self.__values__[index]


    def __setitem__(self, key, value):
        self.set(key, value)


    def __getitem__(self, key):
        return self.get(key)


    def __str__(self):
        return "{}:\n\t{}".format(self.name,
                                  "\n\t".join(map(str, zip(self.__names__, self.__values__))))


    def __length__(self):
        return len(self.__values__)


    def __iter__(self):
        return self


    def next(self):  # Python 3: def __next__(self)
        if self.__current__ > len(self.__values__) - 1:
            self.__current__ = 0
            raise StopIteration
        else:
            self.__current__ += 1
            return self.__values__[self.__current__]

class Regfile(Storage):

    def __init__(self, *args, **kwargs):
        """ :param name: decides the type of __values__ to make. either one of: "gp", "e", "c", "fp" """
        # if someString in initializers:
        super(Storage, self).__init__(*args, **kwargs)

        self.__values__[1] = 1  # DEBUG: FIXME: just for testing

class Mem(Storage):
    def __init__(self, *args, **kwargs):
        """ :param name: decides the type of __values__ to make. either one of: "gp", "e", "c", "fp" """
        super().__init__(*args, **kwargs)


    def set(self, address, byteElements):
        for b in [byteElements]:  # if multiple elements
            self.__values__[address] = b
            address += 1

