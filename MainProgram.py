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


    def step(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")

        if self.pc >= len(self.assembledFile.directiveSegments.get('.text')):
            print("reached end of .text segment")
            return
        next_instruction = self.assembledFile.directiveSegments.get('.text')[self.pc]
        self.executeInstruction(next_instruction)
        self.pc += 1
        self.redisplayReg()
        self.redisplayMem()

    def runAll(self):
        if self.assembledFile is None:
            raise Exception("no assembled file, must compile")        
        else :
            for x in self.assembledFile.directiveSegments.get('.text',[]):
                instr = instr = self.assembledFile.directiveSegments.get('.text', [])[self.currentInst]
                self.executeInstruction(instr)
                print("Step(), instr: " + str(instr) + "\nRegFile: " + str(self.regfile.__regs__))
                self.currentInst += 1
            self.redisplayReg()
            self.redisplayMem()  
    def redisplayReg(self):
        if self.gui is None:
            raise Exception("No gui object")
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
    def redisplayMem(self):
        #This is a naaive way it can be optimized, no time
        self.gui.openScrollPane("memPane")
        index = 0
        for x in sim.mem.theBytes:
            name = str(index) + "c1"
            self.gui.setLabel(name, sim.mem.theBytes[index])
            index +=1
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


        def __init__(self, initStr: str):
            """ :param initStr: decides the type of regfile to make. either one of: "gp", "e", "c", "fp" """
            # if someString in initializer:
            length, names, representations = Simulator.Regfile.initializer.get(initStr)

            self.names = names
            self.regfile = [0] * length
            self.representations = representations

            print("regfile:", self.regfile)


        def set(self, index, newVal, instruction: Instruction = None):
            if type(index) is str:  # this line allows for indexing by reg names (as strings)
                index = self.names.index(index)

            print("setting reg {}: {} -> {}".format(index, self.regfile[index], newVal))
            self.regfile[index] = newVal


        def get(self, regIndex: int):
            return self.regfile[regIndex]

    class Mem:
        def __init__(self):
           self.theBytes = ["00000000"]*256


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
    def redisplayReg():
        app.setLabel("Registers", "R0 = " + str(sim.regfile.get(0)) + "     \nR1 = " + str(sim.regfile.get(1)) + "   \nR2 = " + str(sim.regfile.get(2))+ 
                            "\nR3 = " + str(sim.regfile.get(3)) + " \nR4 = " + str(sim.regfile.get(4)) + "      \nR5 = " + str(sim.regfile.get(5))+
                            "\nR6 = " + str(sim.regfile.get(6)) + " \nR7 = " + str(sim.regfile.get(7)) + "      \nR8 = " + str(sim.regfile.get(8))+
                            "\nR9 = " + str(sim.regfile.get(9)) + " \nR10 = " + str(sim.regfile.get(10)))
        app.setLabel("Registers1", "R11 = " + str(sim.regfile.get(11)) + "     \nR12 = " + str(sim.regfile.get(12)) + "   \nR13 = " + str(sim.regfile.get(13))+ 
                            "\nR14 = " + str(sim.regfile.get(14)) + " \nR15 = " + str(sim.regfile.get(15)) + "      \nR16 = " + str(sim.regfile.get(16))+
                            "\nR17 = " + str(sim.regfile.get(17)) + " \nR18 = " + str(sim.regfile.get(18)) + "      \nR19 = " + str(sim.regfile.get(19))+
                            "\nR18 = " + str(sim.regfile.get(20)) + " \nR21 = " + str(sim.regfile.get(21)))
        app.setLabel("Registers2", "R22 = " + str(sim.regfile.get(22)) + "     \nR23 = " + str(sim.regfile.get(23)) + "   \nR24 = " + str(sim.regfile.get(24))+ 
                            "\nR25 = " + str(sim.regfile.get(25)) + " \nR26 = " + str(sim.regfile.get(26)) + "      \nR27 = " + str(sim.regfile.get(17))+
                            "\nR28 = " + str(sim.regfile.get(28)) + " \nR29 = " + str(sim.regfile.get(29)) + "      \nR30 = " + str(sim.regfile.get(30))+ "\nR31 = " + str(sim.regfile.get(31)))
    def redisplayMem():
        #This is a naaive way it can be optimized, no time
        app.openScrollPane("memPane")
        index = 0
        for x in sim.mem.theBytes:
            name = str(index) + "c1"
            app.setLabel(name, sim.mem.theBytes[index])
            index +=1
        app.stopScrollPane()
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
        if(name=="Compile"):
           sim.__init__(compileASM_GUI(),app)
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
        app.setLabelBg(name,("grey"))
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
    if cmd_args.r and _assembledFile:
        sim.init(_assembledFile)
        sim.step()
elif cmd_args.asm:
    _assembledFile = compileASM(cmd_args.asm)

    if cmd_args.r and _assembledFile:
        sim.init(_assembledFile)
        sim.step()
else:
    Tk().withdraw()
    frame = makeGUI()
