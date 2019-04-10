

from tkinter import *
import re

# from tkFileDialog import *
from tkinter import filedialog
import os.path
from argparse import ArgumentParser
import sys
from tkinter.filedialog import askopenfilename, asksaveasfilename
import Assembler


filename = "Untitled"
fileexists = False
symbolTable = {}
global currentLine


def compileASM(asm_text):
    global filename
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
            cpu_out += str(i) + " => x\"" + Assembler.decode(line) + "\",\n"

    # print cpu_out
    name, ext = os.path.splitext(filename)
    hexfilename = name + ".hex"
    hexfile = open(hexfilename, "w")
    hexfile.seek(0)
    hexfile.truncate()
    hexfile.write(cpu_out)
    print(cpu_out)
    hexfile.close()


def main():
    # Assembler Main code

    # argument parsing
    parser = ArgumentParser()
    parser.add_argument('--file', type=str, default="", help='path to the file program file (optional)')
    cmd_args = parser.parse_args()

    file = cmd_args.file

    # if the user passed a valid filepath, then don't run GUI and just compile it in the command line
    if file and os.path.isfile(file):
        file = open(file)
        compileASM(file.read())
    else:
        Tk().withdraw()
        frame = makeGUI()
    return


def makeGUI():
    frame = Toplevel()
    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    frame.title("M-Architecture Assembler [" + filename + "]")
    textArea = Text(frame, height=30, width=100, padx=3,
                    pady=3, yscrollcommand=scrollbar.set)
    textArea.pack(side=RIGHT)
    scrollbar.config(command=textArea.yview)

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
        return compileASM(textArea.get("1.0", END))


    menubar = Menu(frame)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=openFile)
    filemenu.add_command(label="Save", command=saveFile, state=DISABLED)
    filemenu.add_command(label="Save as...", command=saveFileAs)
    filemenu.add_command(label="Exit", command=exitApp)
    menubar.add_cascade(label="File", menu=filemenu)
    runmenu = Menu(menubar, tearoff=0)
    runmenu.add_command(label="Compile", command=compileASM_GUI)
    menubar.add_cascade(label="Run", menu=runmenu)
    frame.config(menu=menubar)
    frame.minsize(750, 450)
    frame.maxsize(750, 450)
    frame.mainloop()
    return frame


if __name__ == '__main__':
    main()
