from tkinter import *
import re
# from tkFileDialog import *
from tkinter import filedialog
import os.path
from argparse import ArgumentParser
import sys
from tkinter.filedialog import askopenfilename, asksaveasfilename
import Assembler
from Addressable import *
from AssembledFile import AssembledFile

import sys
from time import time

sys.path.append("appJar/")
from appjar import gui


class Simulator:
    def __init__(self, assembledFile=None):
        self.regfile = Simulator.Regfile("gp")
        self.mem = Simulator.Mem()
        self.currentInst = 0
        self.assembledFile = assembledFile
        Simulator.sim = self


    def init(self, assembledFile: AssembledFile):
        """ resets the simulator, preparing it for a new file """
        self.__init__(assembledFile)
        # reset memory and stuff


    def step(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")
        pass


    def runAll(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")
            pass

    class Regfile:
        # (width in bits)
        initializer = {
            "gp": 32,
            "e": 64,
            "c": 64,
            "fp": 64
        }


        def __init__(self, someString):
            # if someString in initializer:
            self.regfile = [0] * 32


        def set(self, index, newVal):
            self.regfile[index] = newVal


        def get(self, x):
            return self.regfile[x]

    class Mem:
        # def __init__(se)

        def __init__(self):
            self.theBytes = [0] * 256


        # self.regfile = {
        #     'gp':gprf,
        #     'fp':regFile
        # }
        #  = Regfile(names={}, regwidth=32)
        # self.mem
        pass

    def executeInstruction(self, instruction: Instruction):
        instruction.execute(self)


filename = "Untitled"
fileexists = False
symbolTable = {}
global currentLine
sim = None


def compileASM(asm_text):
    assembledFile = AssembledFile(asm_text)
    cpu_out = ""
    asmlines = re.split("\n", asm_text)
    for i in range(len(asmlines)):
        line = asmlines[i].split('//')[0].strip()  # discard comments

        if line == "":
            # instruction
            continue

        if line[0] == '.':  # directive
            # todo:
            continue
        elif line[0] == "@":  # label
            if line in symbolTable:
                raise Exception('Duplicate symbol "' + line + '" at line: ' + str(i))
            symbolTable[line] = i
        else:  # instruction

            # try:
            cpu_out += str(i) + " => x\"" + Assembler.decodeToHex(line) + "\",\n"
            # except Exception as e:
            #     print('Exception:'
            #           '\nwhile decoding instruction: "{}"'
            #           '\nThe issue is that:\n\n{}'.format(str(line), str(e)))

    # print cpu_out
    name, ext = os.path.splitext(filename)
    hexfilename = name + ".hex"
    hexfile = open(hexfilename, "w")
    hexfile.seek(0)
    hexfile.truncate()
    hexfile.write(cpu_out)
    print(cpu_out)
    hexfile.close()

    print("AssembledFile:" + assembledFile.text)
    return assembledFile


def makeGUI():
    def openFile():
        global filename
        openfilename = askopenfilename()
        if openfilename is not None:
            filename = openfilename
            asmfile = open(filename, "r")
            asmfile.seek(0)
            asmdata = asmfile.read()
            textArea.delete("1.0", "end - 1c")
            textArea.insert("1.0", asmdata)
            asmfile.close()
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + filename + "]")
            frame.focus()


    def saveFile():
        global filename
        asmdata = textArea.get("1.0", "end - 1c")
        asmfile = open(filename, "w")
        asmfile.seek(0)
        asmfile.truncate()
        asmfile.write(asmdata)
        asmfile.close()


    def saveFileAs():
        global filename
        global fileexists
        saveasfilename = asksaveasfilename()
        if saveasfilename is not None:
            filename = saveasfilename
            fileexists = True
            asmdata = textArea.get("1.0", "end - 1c")
            asmfile = open(filename, "w")
            asmfile.seek(0)
            asmfile.truncate()
            asmfile.write(asmdata)
            asmfile.close()
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + filename + "]")
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


    def toolPress(name):
        if name == "Compile":
            sim.init(compileASM_GUI())
            print("#ToDo compile")
        elif name == "Execute":
            sim.step()
            print("#ToDo Execute")
        elif name == "Execute Next":
            print("#ToDo Execute Next")


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
    app.addLabel("Registers", "R1 = " + str(r1) + "\tR2 = " + str(r2) + "\tR3 = " + str(r3) + "\nR4 = " + str(r4), 0, 1,
                 1)
    app.addLabel("Registers1", "R1 = " + str(r1) + "\nR2 = " + str(r2) + "\nR3 = " + str(r3) + "\nR4 = " + str(r4), 0,
                 2, 1)
    app.addLabel("Registers2", "R1 = " + str(r1) + "\nR2 = " + str(r2) + "\nR3 = " + str(r3) + "\nR4 = " + str(r4), 0,
                 3, 1)
    # app.addLabel("Memory", "Memory Content", 1, 0, 3)
    app.startScrollPane("PANE")
    for x in range(1000):
        name = str(x)
        app.addLabel(name, name, row=x)
        app.addLabel(name + "c1", "Memory content to be inserted here", row=x, column=1, colspan=4)
        app.setLabelBg(name, "grey")
    app.stopScrollPane()

    app.setLabel("Registers", "R0 = " + str(r1) + "     \nR1 = " + str(r2) + "   \nR2 = " + str(r3) +
                 "\nR3 = " + str(r4) + " \nR4 = " + str(r2) + "      \nR5 = " + str(r3) +
                 "\nR6 = " + str(r4) + " \nR7 = " + str(r2) + "      \nR8 = " + str(r3) +
                 "\nR9 = " + str(r4) + " \nR10 = " + str(r2))
    app.setLabel("Registers1", "R11 = " + str(r1) + "     \nR12 = " + str(r2) + "   \nR13 = " + str(r3) +
                 "\nR14 = " + str(r4) + " \nR15 = " + str(r2) + "      \nR16 = " + str(r3) +
                 "\nR17 = " + str(r4) + " \nR18 = " + str(r2) + "      \nR19 = " + str(r3) +
                 "\nR18 = " + str(r4) + " \nR21 = " + str(r2))
    app.setLabel("Registers2", "R22 = " + str(r1) + "     \nR23 = " + str(r2) + "   \nR24 = " + str(r3) +
                 "\nR25 = " + str(r4) + " \nR26 = " + str(r2) + "      \nR27 = " + str(r3) +
                 "\nR28 = " + str(r4) + " \nR29 = " + str(r2) + "      \nR30 = " + str(r3) +
                 "\nR31 = " + str(r4))
    # app.setLabelBg("Input", "white")
    app.setLabelBg("Registers", "grey")
    app.setLabelBg("Registers2", "grey")
    # app.setLabelBg("Memory", "Red")

    tools = ["Compile", "Execute", "Execute Next"]
    app.addToolbar(tools, toolPress)
    # app.showSplash("M-Architecture Simulator", fill='blue', stripe='black', fg='white', font=44)
    app.go()


# Assembler Main code

# argument parsing
parser = ArgumentParser()
parser.add_argument('--file', type=str, default="", help='path to the file program file (optional)')
parser.add_argument('--asm', type=str, default="", help='instruction to assemble')
parser.add_argument('-r', default=False, action="store_true", help='run after assembling')
cmd_args = parser.parse_args()

file = cmd_args.file

sim = Simulator()

# if the user passed a valid filepath, then don't run GUI and just compile it in the command line
if file and os.path.isfile(file):
    file = open(file)
    _assembledFile = compileASM(file.read())
    sim.init(_assembledFile)
elif cmd_args.asm:
    _assembledFile = compileASM(cmd_args.asm)
    if cmd_args.r and _assembledFile:
        sim.init(_assembledFile)
        sim.step()
else:
    Tk().withdraw()
    frame = makeGUI()
