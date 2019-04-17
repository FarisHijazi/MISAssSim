import os.path
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

from AssembledFile import AssembledFile
from Simulator import Simulator
from appjar import gui

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


def makeGUI(text):
    app = gui("M-Architecture Simulation ", "800x675")
    app.setSticky("news")
    app.setExpand("both")
    app.setFont(14)



    def redisplayMem():
        # This is a naaive way it can be optimized, no time
        app.openScrollPane("memPane")
        for index in range(len(sim.mem.theBytes)):
            name = str(index) + "c1"
            app.setLabel(name, sim.mem.theBytes[index])
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
        return compileASM(app.getTextArea("code"))


    def menuPress(name):
        print("Hello")
        if name == "Open":
            print("Open")
        elif name == "Close":
            app.stop()

    app.addScrolledTextArea("code", 0, 0, 2, text=text)


    def toolPress(name):
        if name == "Compile":
            sim.init(compileASM_GUI(), app)
        elif name == "Execute":
            sim.runAll()
        elif name == "Execute Next":
            sim.step()


    fileMenus = ["Open", "Save", "Save as...", "-", "Close"]
    app.addMenuList("File", fileMenus, menuPress)

    app.startScrollPane("regs")
    for i, name, value, rep in sim.sim.regfile.items():
        # app.addLabel(name + "_name", text=name, row=i, column=1, colspan=1, selectable=False)
        app.addLabelEntry(name, row=i, column=2, colspan=6)
        app.setEntry(name, value)
        app.addLabel(name + "_rep", text=rep, row=i, column=3, colspan=1, selectable=False)
        # app.addLabel("{0}regs".format(i), "", row=i, column=1, colspan=4)
        # app.setLabel(name, sim.regfile[i])
    app.stopScrollPane()

    # Parameters passed are (row    column  columnSpan)
    app.startScrollPane("memPane")
    for x in range(len(sim.mem.theBytes)):
        app.addLabel(str(x), text=str(x), row=x)
        app.addLabel("{0}c1".format(x), "", row=x, column=1, colspan=4)
        app.setLabelBg(str(x), "grey")
    app.stopScrollPane()


    sim.redisplayReg()
    redisplayMem()

    # app.setLabelBg("Registers", "grey")
    # app.setLabelBg("Registers2", "grey")

    tools = ["Compile", "Execute", "Execute Next"]
    app.addToolbar(tools, toolPress)
    # app.showSplash("M-Architecture Simulator", fill='blue', stripe='black', fg='white', font=44)
    app.go()


# Assembler Main code

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', type=argparse.FileType('r'), help='path to the file program file (optional)')
parser.add_argument('-i', '--asm', type=str, default="",
                    help="Assembly instruction(s) to assemble (separate with ';' as new line)")
parser.add_argument('-t', '--text', default=False, action="store_true", help='Text mode')  # text mode
parser.add_argument('-r', '--run', default=False, action="store_true",
                    help='run after assembling (only for cmd mode (non-gui))')
# parser.add_argument('-ng', '--no-gui', default=False, action="store_true", help='run without gui (disabled by default)')
cmd_args = parser.parse_args()

_assembledFile: AssembledFile
sim = Simulator()

# if the user passed a valid filepath, then don't run GUI and just compile it in the command line


if cmd_args.text:
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

if cmd_args.file:
    _assembledFile = compileASM(cmd_args.file.read())
    # cmd_args.file = file

    sim.init(_assembledFile)

# if assembly text was passed (separate with ';')'
if cmd_args.asm:
    instructions = cmd_args.asm.split(';')
    print("instructions:", instructions)
    asm = "\n".join(instructions)

    _assembledFile = compileASM(asm)


if not cmd_args.run:
    text = ""
    if cmd_args and cmd_args.file:
        text = cmd_args.file.read()
    if cmd_args and cmd_args.asm:
        text = cmd_args.asm

    # clear args so that appjar wouldn't get messed up
    sys.argv = [sys.argv[0]]

    Tk().withdraw()
    frame = makeGUI(text)

elif _assembledFile:
    sim.init(_assembledFile)
    sim.runAll()
