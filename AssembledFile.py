from typing import List, Dict
from Addressable import *


def reGroup(match):
    return match if not match else match.group()


class AssembledFile:
    # data directive: size in bytes
    def __init__(self, text):
        # initializations:
        self.text = text
        self.directiveSegments = {
            ".text": [],  # Instruction - defines a text segment that contains read-only executable instructions
            ".data": [],  # (elementSize, elements[]) defines a data segment that contains read/write data
            ".stext": [],  # Instruction - defines a system text segment that contains system instructions
            ".sdata": [],  # defines a system data segment that contains read/write system data
        }
        # self.symbolTable: Dict[str, Addressable]  # label: Addressable
        self.symbolTable = {}  # label: Addressable

        # assembling the file

        self.hex = []
        asmlines = re.split("\n", self.text)
        currentSegment = ".text"

        # #Steps for checking a line:
        # assuming only one directive per line
        # 1. parse label
        # 2. parse directive
        # 3. specific parsing depending on the segment
        # .data
        #   1. parse type (.byte etc...)
        #   2. get args ('A', 5, 234, 's', 'r', 'i' ...)

        i_counter = 0  # instruction counter for assembling the code (fake counter to keep track of instructions), used to calculate relative addresses
        next_align = 'auto'
        for i in range(len(asmlines)):
            line = asmlines[i].split('//')[0].strip()  # discard comments

            # parsing
            segmentDirective_match = re.search("|".join(self.directiveSegments.keys()), line)
            directive_match = re.search(r'\.[a-zA-z][a-zA-z\d_]+', line)
            label_match = re.search(r'^@[a-zA-z][a-zA-z\d_]+', line)  # early label
            dataDirective_match = re.search(r'\.' + "|".join(DataBlock.directives.keys()), line)

            if line and label_match:  # label
                if line in self.symbolTable:
                    raise Exception('Duplicate symbol "' + line + '" at line: ' + str(i))

                self.symbolTable[label_match.group().strip()] = Addressable(size=0,
                                                                            lineStr=line)  # store the address of the label as an Addressable with size=0

            # update current segment
            elif line and directive_match and line in self.directiveSegments:
                currentSegment = directive_match.group().strip()

            # storing the data
            if line and currentSegment in [".data", ".sdata"]:
                align_match = re.search(r'\.align\s+(\d+)]+', line)  # '.align 3'
                if align_match:
                    next_align = int(align_match.groups()[0])
                elif line not in self.directiveSegments:
                    dataBlock = DataBlock(lineStr=line, alignment=next_align)
                    self.directiveSegments.get(currentSegment).append(dataBlock)

            elif line and currentSegment == ".text" and not directive_match:  # .text cannot be in the same line as an instruction
                # instruction
                instr = Instruction(line)

                print('{0} => {1} => x"{2}",\n'.format(str(i), str(instr), instr.hex()))
                self.hex.append(instr.hex())

                self.directiveSegments[currentSegment] += [instr]

            print('{}:\t"{}"'
                  '\n\tsegment: {}'
                  '\n\tdirective: {}'
                  '\n\tlabel: {}\n'.format(i, line, currentSegment, reGroup(segmentDirective_match),
                                           reGroup(directive_match),
                                           reGroup(label_match)))

            # TODO: increment current line and current address

        print("Successfully assembled file:", self)


    def __str__(self):
        return "AssembledFile: ( {} )".format(self.directiveSegments)


def extractDirective(lineStr: str):
    """ :param lineStr:
    :return: (directive, directiveArgs) """
    match = re.search(r'\.[a-zA-z][a-zA-z\d_]+', lineStr)
    return match if not match else match.group()


