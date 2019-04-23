import os.path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import ConversionUtils
from AssembledFile import AssembledFile
from Simulator import Simulator
from appjar import gui

sim = None

def compileASM(asm_text, outfile="output"):
    assembledFile = AssembledFile(asm_text)
    # print cpu_out
    fname, ext = os.path.splitext(outfile)

    # writing binary data to file
    with open(fname + ".bin", "wb") as binfile:
        binfile.seek(0)
        binfile.truncate()
        for word in map(lambda x: ConversionUtils.long_to_bytes(int(x, base=16)), assembledFile.hex):
            binfile.write(word)

    # writing hex string file
    with open(fname + ".hex", "w") as hexfile:
        hexfile.seek(0)
        hexfile.truncate()
        hexfile.write("\n".join(assembledFile.hex))

    print(assembledFile.hex)
    return assembledFile


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


    def menuPress(name):
        if name == "Open":
            print("Open")
            fileLocation = app.openBox(title=None, dirName=None, fileTypes=[('text', '*.txt')], asFile=False, parent=None)
            fileObject = open(fileLocation,"r")
            code = fileObject.read()
            app.setTextArea("code", code)
        
        elif name == "Save as...":
            fileLocation = app.saveBox(title="Save as...", fileName=None, dirName=None, fileExt=".txt", fileTypes=None, asFile=None, parent=None)
            fileObject = open(fileLocation,"w")
            fileObject.write(app.getTextArea("code"))

        elif name == "Close":
            app.stop()


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
parser.add_argument('-f', '--file', nargs='?', type=str, default='untitled_program',
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
