from tkinter import *
import re
import os.path
from argparse import ArgumentParser
from tkinter.filedialog import askopenfilename, asksaveasfilename
from Addressable import *
from AssembledFile import AssembledFile

import sys

from appjar import gui


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
        print('step() Run instr: "{0}"\nRegFile: {1}'.format(str(next_instruction), str(self.regfile)))
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
                    print('Running instr: "{0}"\nRegFile: {1}'.format(str(instr), str(self.regfile)))
                    self.pc += 1

            self.redisplayReg()
            self.redisplayMem()


    def redisplayMem(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            #This is a naaive way it can be optimized, no time
            self.gui.openScrollPane("memPane")
            index = 0
            for x in sim.mem.theBytes:
                name = str(index) + "c1"
                self.gui.setLabel(name, sim.mem.theBytes[index])
                index += 1
                self.gui.stopScrollPane()
                raise Exception("no assembled file, must compile")


    def redisplayReg(self):
        if self.gui is None:
            # raise Exception("No gui object")
            print("Register content:".format(self.regfile))
        else:
            self.gui.setLabel("Registers", "R0 = " + str(self.regfile.get(0)) + "     \nR1 = " + str(self.regfile.get(1)) + "   \nR2 = " + str(self.regfile.get(2))+
                                "\nR3 = " + str(self.regfile.get(3)) + " \nR4 = " + str(self.regfile.get(4)) + "      \nR5 = " + str(self.regfile.get(5))+
                                "\nR6 = " + str(self.regfile.get(6)) + " \nR7 = " + str(self.regfile.get(7)) + "      \nR8 = " + str(self.regfile.get(8))+
                                "\nR9 = " + str(self.regfile.get(9)) + " \nR10 = " + str(self.regfile.get(10)))
            self.gui.setLabel("Registers1", "R11 = " + str(self.regfile.get(11)) + "     \nR12 = " + str(self.regfile.get(12)) + "   \nR13 = " + str(self.regfile.get(13))+
                                "\nR14 = " + str(self.regfile.get(14)) + " \nR15 = " + str(self.regfile.get(15)) + "      \nR16 = " + str(self.regfile.get(16))+
                                "\nR17 = " + str(self.regfile.get(17)) + " \nR18 = " + str(self.regfile.get(18)) + "      \nR19 = " + str(self.regfile.get(19))+
                                "\nR18 = " + str(self.regfile.get(20)) + " \nR21 = " + str(self.regfile.get(21)))
            self.gui.setLabel("Registers2", "R22 = " + str(self.regfile.get(22)) + "     \nR23 = " + str(self.regfile.get(23)) + "   \nR24 = " + str(self.regfile.get(24))+
                                "\nR25 = " + str(self.regfile.get(25)) + " \nR26 = " + str(self.regfile.get(26)) + "      \nR27 = " + str(self.regfile.get(17))+
                                "\nR28 = " + str(self.regfile.get(28)) + " \nR29 = " + str(self.regfile.get(29)) + "      \nR30 = " + str(self.regfile.get(30))+ "\nR31 = " + str(sim.regfile.get(31)))

            for i in range(len(sim.mem.theBytes)):
                name = str(i) + "c1"
                self.gui.setLabel(name, sim.mem.theBytes[i])

            self.gui.stopScrollPane()


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



outfile = "hex"
sim = None


def compileASM(asm_text):
    assembledFile = AssembledFile(asm_text)
    # print cpu_out
    name, ext = os.path.splitext(outfile)

    with open(name + ".hex", "wb") as hexfile:
        hexfile.seek(0)
        hexfile.truncate()
        for word in map(lambda x: long_to_bytes(int(x, base=16)), assembledFile.hex):
            hexfile.write(word)
        hexfile.close()

    print(assembledFile.hex)

    print("AssembledFile:" + assembledFile.text)
    return assembledFile


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


def makeGUI():
    app = gui("M-Architecture Simulation ", "800x675")
    app.setSticky("news")
    app.setExpand("both")
    app.setFont(14)


    def redisplayReg():
        app.setLabel("Registers",
                     "R0 = " + str(sim.regfile.get(0)) + "     \nR1 = " + str(sim.regfile.get(1)) + "   \nR2 = " + str(
                         sim.regfile.get(2)) +
                     "\nR3 = " + str(sim.regfile.get(3)) + " \nR4 = " + str(sim.regfile.get(4)) + "      \nR5 = " + str(
                         sim.regfile.get(5)) +
                     "\nR6 = " + str(sim.regfile.get(6)) + " \nR7 = " + str(sim.regfile.get(7)) + "      \nR8 = " + str(
                         sim.regfile.get(8)) +
                     "\nR9 = " + str(sim.regfile.get(9)) + " \nR10 = " + str(sim.regfile.get(10)))
        app.setLabel("Registers1", "R11 = " + str(sim.regfile.get(11)) + "     \nR12 = " + str(
            sim.regfile.get(12)) + "   \nR13 = " + str(sim.regfile.get(13)) +
                     "\nR14 = " + str(sim.regfile.get(14)) + " \nR15 = " + str(
            sim.regfile.get(15)) + "      \nR16 = " + str(sim.regfile.get(16)) +
                     "\nR17 = " + str(sim.regfile.get(17)) + " \nR18 = " + str(
            sim.regfile.get(18)) + "      \nR19 = " + str(sim.regfile.get(19)) +
                     "\nR18 = " + str(sim.regfile.get(20)) + " \nR21 = " + str(sim.regfile.get(21)))
        app.setLabel("Registers2", "R22 = " + str(sim.regfile.get(22)) + "     \nR23 = " + str(
            sim.regfile.get(23)) + "   \nR24 = " + str(sim.regfile.get(24)) +
                     "\nR25 = " + str(sim.regfile.get(25)) + " \nR26 = " + str(
            sim.regfile.get(26)) + "      \nR27 = " + str(sim.regfile.get(17)) +
                     "\nR28 = " + str(sim.regfile.get(28)) + " \nR29 = " + str(
            sim.regfile.get(29)) + "      \nR30 = " + str(sim.regfile.get(30)) + "\nR31 = " + str(sim.regfile.get(31)))


    def redisplayMem():
        # This is a naaive way it can be optimized, no time
        app.openScrollPane("memPane")
        index = 0
        for x in sim.mem.theBytes:
            name = str(index) + "c1"
            app.setLabel(name, sim.mem.theBytes[index])
            index += 1
        app.stopScrollPane()


    def openFile():
        global outfile
        openfilename = askopenfilename()
        if openfilename is not None:
            outfile = openfilename
            asmfile = open(outfile, "r")
            asmfile.seek(0)
            asmdata = asmfile.read()
            textArea.delete("1.0", "end - 1c")
            textArea.insert("1.0", asmdata)
            asmfile.close()
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + outfile + "]")
            frame.focus()


    def saveFile():
        global outfile
        asmdata = textArea.get("1.0", "end - 1c")
        asmfile = open(outfile, "w")
        asmfile.seek(0)
        asmfile.truncate()
        asmfile.write(asmdata)
        asmfile.close()


    def saveFileAs():
        global outfile
        saveasfilename = asksaveasfilename()
        if saveasfilename is not None:
            outfile = saveasfilename
            asmdata = textArea.get("1.0", "end - 1c")
            asmfile = open(outfile, "w")
            asmfile.seek(0)
            asmfile.truncate()
            asmfile.write(asmdata)
            asmfile.close()
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + outfile + "]")
            frame.focus()


    def exitApp():
        frame.destroy()
        sys.exit()


    def compileASM_GUI():
        return compileASM(app.getTextArea("title"))


    def menuPress(name):
        print("Hello")
        if name == "Open":
            print("Open")
        elif name == "Close":
            app.stop()


    fileMenus = ["Open", "Save", "Save as...", "-", "Close"]
    app.addMenuList("File", fileMenus, menuPress)
    r1 = 3
    r5 = 2
    r2 = 2
    r3 = 9
    r4 = 10
    # Parameters passed are (row    column  columnSpan)
    # app.addLabel("Input", "Input Assembly code here", 0, 0, 2)
    app.addScrolledTextArea("title", 0, 0, 2, text="Input code here")
    app.addLabel("Registers", "R1 = " + str(r1) + "\tR2 = " + str(r2) + "\tR3 = " + str(r3) + "\nR4 = " + str(r4), 0, 1,
                 1)
    app.addLabel("Registers1", "R1 = " + str(r1) + "\nR2 = " + str(r2) + "\nR3 = " + str(r3) + "\nR4 = " + str(r4), 0,
                 2, 1)
    app.addLabel("Registers2", "R1 = " + str(r1) + "\nR2 = " + str(r2) + "\nR3 = " + str(r3) + "\nR4 = " + str(r4), 0,
                 3, 1)
    # app.addLabel("Memory", "Memory Content", 1, 0, 3)
    app.startScrollPane("memPane")
    for x in range(len(sim.mem.theBytes)):
        name = str(x)
        app.addLabel(name, name, row=x)
        app.addLabel(name + "c1", "Memory content to be inserted here", row=x, column=1, colspan=4)
        app.setLabelBg(name, "grey")
    app.stopScrollPane()


    def toolPress(name):
        if name == "Compile":
            sim.__init__(compileASM_GUI(), app)
        elif name == "Execute":
            sim.runAll()
        elif name == "Execute Next":
            sim.step()


    app = gui("M-Architecture Simulation ", "800x675")
    app.setSticky("news")
    app.setExpand("both")
    app.setFont(14)

    fileMenus = ["Open", "Save", "Save as...", "-", "Close"]
    app.addMenuList("File", fileMenus, menuPress)
    r1 = 3
    r5 = 2
    r2 = 2
    r3 = 9
    r4 = 10
    # Parameters passed are (row    column  columnSpan)
    # app.addLabel("Input", "Input Assembly code here", 0, 0, 2)
    app.addScrolledTextArea("title", 0, 0, 2, text="Input code here")
    app.addLabel("Registers", "", 0, 1, 1)
    app.addLabel("Registers1", "", 0, 2, 1)
    app.addLabel("Registers2", "", 0, 3, 1)
    app.startScrollPane("memPane")
    for x in range(1000):
        name = str(x)
        app.addLabel(name, name, row=x)
        app.addLabel(name + "c1", "Memory content to be inserted here", row=x, column=1, colspan=4)
        app.setLabelBg(name, ("grey"))
    app.stopScrollPane()
    redisplayReg()
    redisplayMem()

    app.setLabelBg("Registers", "grey")
    app.setLabelBg("Registers2", "grey")

    tools = ["Compile", "Execute", "Execute Next"]
    app.addToolbar(tools, toolPress)
    # app.showSplash("M-Architecture Simulator", fill='blue', stripe='black', fg='white', font=44)
    app.go()


# Assembler Main code

# argument parsing
parser = ArgumentParser()
parser.add_argument('-f', '--file', type=str, default="", help='path to the file program file (optional)')
parser.add_argument('-i', '--asm', type=str, default="", help="Assembly instruction(s) to assemble (separate with ';' as new line)")
parser.add_argument('-t', '--text', default=False, action="store_true", help='Text mode')  # text mode
parser.add_argument('-r', '--run', default=False, action="store_true", help='run after assembling')
cmd_args = parser.parse_args()

file = cmd_args.file

sim = Simulator()

# if the user passed a valid filepath, then don't run GUI and just compile it in the command line
if file and os.path.isfile(file):
    file = open(file)
    _assembledFile = compileASM(file.read())

    sim.init(_assembledFile)

    if cmd_args.run and _assembledFile:
        sim.init(_assembledFile)
        sim.runAll()
elif cmd_args.text:
    accumulatedInput = ""

    def runAll():
        _assembledFile = compileASM(accumulatedInput)
        sim.init(_assembledFile)
        sim.runAll()

    def compile():
        _assembledFile = compileASM(accumulatedInput)
        sim.init(_assembledFile)


    'name: (description:str, mnemonics:List[str], func)'
    commands = dict(
        run=dict(description="compile and run everything", cmd=['r', 'run'], func=runAll),
        compile=dict(description="compile", cmd=['c', 'compile'], func=compile),
        step=dict(description='execute only the next line', cmd=['p', 'step'], func=sim.step),
        exit=dict(description='exit the program', cmd=['q', 'quit', 'exit', 'x'], func=exit)
    )
    print("Text mode: Write your program or load it from a file")
    print("use '$' followed by a command:\n\t{}\n\n".format(
        "\t\n".join(map(lambda k: '"{}" {}:   {}'.format(
            k, commands[k].get('cmd'), commands[k].get('description')), commands.keys()))
    ))

    i = 1
    while True:
        ipt = input("{}:... ".format(i))
        # check if command:
        if ipt and ipt[0] == '$':
            for command in commands:
                if ipt[1:] in commands.get(command).get('cmd'):
                    commands[command].get('func')()

        else:
            accumulatedInput += ipt + '\n'
            i += 1

# if assembly text was passed (separate with ';')'
elif cmd_args.asm:
    instructions = cmd_args.asm.split(';')
    print("instructions:", instructions)
    asm = "\n".join(instructions)

    _assembledFile = compileASM(asm)

    if cmd_args.run and _assembledFile:
        sim.init(_assembledFile)
        sim.runAll()
else:
    Tk().withdraw()
    frame = makeGUI()
