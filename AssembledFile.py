from Addressable import *
from typing import List, Dict

class AssembledFile:
    def __init__(self):
        self.directives_dict = {
            ".text": List[Addressable],  # defines a text segment that contains read-only executable instructions
            ".data": List[DataBlock],  # defines a data segment that contains read/write data (can be read and written)
            ".stext": List[Addressable],  # defines a system text segment that contains system instructions
            ".sdata": List[DataBlock],  # defines a system data segment that contains read/write system data
        }
        self.symbolTable = Dict[str, Addressable] # label: Addressable



