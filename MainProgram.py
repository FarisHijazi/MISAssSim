import os.path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

from AssembledFile import AssembledFile
from Simulator import Simulator
from appjar import gui

sim = None

def compileASM(asm_text, outfile):
    assembledFile = AssembledFile(asm_text)
    # print cpu_out
    fname, ext = os.path.splitext(outfile)

    # writing binary data to file
    with open(fname + ".bin", "wb") as binfile:
        binfile.seek(0)
        binfile.truncate()
        for word in map(lambda x: long_to_bytes(int(x, base=16)), assembledFile.hex):
            binfile.write(word)

    # writing hex string file
    with open(fname + ".hex", "w") as hexfile:
        hexfile.seek(0)
        hexfile.truncate()
        hexfile.write("\n".join(assembledFile.hex))


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

def makeGUI(cmd_args):
    app = gui("M-Architecture Simulation ", "800x675")
    app.setSticky("news")
    app.setExpand("both")
    app.setFont(14)

    sim.gui = app


    def openFile():
        openfilename = askopenfilename()
        if openfilename is not None:
            cmd_args.outfile = openfilename
            with open(cmd_args.outfile, "r") as asmfile:
                asmfile.seek(0)
                asmdata = asmfile.read()
                textArea.delete("1.0", "end - 1c")
                textArea.insert("1.0", asmdata)
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + cmd_args.outfile + "]")
            frame.focus()


    def saveFile():
        asmdata = textArea.get("1.0", "end - 1c")
        asmfile = open(cmd_args.outfile, "w")
        asmfile.seek(0)
        asmfile.truncate()
        asmfile.write(asmdata)
        asmfile.close()


    def saveFileAs():
        saveasfilename = asksaveasfilename()
        if saveasfilename is not None:
            cmd_args.outfile = saveasfilename
            asmdata = textArea.get("1.0", "end - 1c")
            asmfile = open(cmd_args.outfile, "w")
            asmfile.seek(0)
            asmfile.truncate()
            asmfile.write(asmdata)
            asmfile.close()
            filemenu.entryconfig(filemenu.index("Save"), state=NORMAL)
            frame.title("muCPU Assembler [" + cmd_args.outfile + "]")
            frame.focus()


    def exitApp():
        frame.destroy()
        sys.exit()


    def compileASM_GUI():
        return compileASM(app.getTextArea("code"), cmd_args.outfile)


    def menuPress(name):
        print("Hello")
        if name == "Open":
            print("Open")
        elif name == "Close":
            app.stop()


    app.addScrolledTextArea("code", 0, 0, 2, text=cmd_args.startText)


    def toolPress(name):
        if name == "Compile":
            sim.init(compileASM_GUI(), app)
        elif name == "Execute":
            sim.runAll()
        elif name == "Execute Next":
            sim.step()


    fileMenus = ["Open", "Save", "Save as...", "-", "Close"]
    app.addMenuList("File", fileMenus, menuPress)

    # building regfile gui
    app.startScrollPane(sim.regfile.name, row=0, column=2)
    sim.regfile.buildGUI()

    # building memory gui
    app.startScrollPane(sim.mem.name, row=1)
    sim.mem.buildGUI()

    app.addScrolledTextArea("console", row=1, column=1, colspan=2)

    tools = ["Compile", "Execute", "Execute Next"]
    app.addToolbar(tools, toolPress)
    # app.showSplash("M-Architecture Simulator", fill='blue', stripe='black', fg='white', font=44)
    app.go()

#  code

# === argument parsing ===
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', type=str,
                    help='(optional) path to assembly file, either to be loaded in GUI or to compile in the CLI')
parser.add_argument('-o', '--outfile', nargs='?', type=str, default='$infile$_output',
                    help='(optional) output file name')
parser.add_argument('-i', '--asm', type=str, default="",
                    help="Assembly instruction(s) to assemble (separate with ';' as new line)")
parser.add_argument('-t', '--text', default=False, action="store_true", help='Text mode')  # text mode
parser.add_argument('-r', '--run', default=False, action="store_true",
                    help='run after assembling (only for cmd mode (non-gui))')
# parser.add_argument('-ng', '--no-gui', default=False, action="store_true", help='run without gui (disabled by default)')
cmd_args = parser.parse_args()

_assembledFile: AssembledFile
sim = Simulator()

cmd_args.outfile = re.sub(r'\$infile\$', cmd_args.file, cmd_args.outfile)

cmd_args.startText = ""

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

# if the user passed a valid filepath, then don't run GUI and just compile it in the command line
if cmd_args.file and os.path.isfile(cmd_args.file):
    with open(cmd_args.file, 'r') as file:
        cmd_args.startText = file.read()
        _assembledFile = compileASM(cmd_args.startText, cmd_args.outfile)
    # cmd_args.file = file

    sim.init(_assembledFile)

# if assembly text was passed (separate with ';')'
if cmd_args.asm:
    instructions = cmd_args.asm.split(';')
    print("instructions:", instructions)
    asm = "\n".join(instructions)

    _assembledFile = compileASM(asm)

if not cmd_args.run:
    if cmd_args and cmd_args.asm:
        print("Reading asm args")
        cmd_args.startText = cmd_args.asm

    sys.argv = [sys.argv[0]]  # clear args so that appjar wouldn't get messed up

    Tk().withdraw()
    frame = makeGUI(cmd_args)
elif _assembledFile:
    sim.init(_assembledFile)
    sim.runAll()
