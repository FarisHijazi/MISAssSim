from typing import List, Dict
from Addressable import *

class AssembledFile:
    def __init__(self, text):
        self.text = text
        self.directiveSegments = {
            ".text": List,  # defines a text segment that contains read-only executable instructions
            ".data": List[DataBlock],  # defines a data segment that contains read/write data (can be read and written)
            ".stext": List,  # defines a system text segment that contains system instructions
            ".sdata": List[DataBlock],  # defines a system data segment that contains read/write system data
        }
        self.symbolTable = Dict[str, Addressable] # label: Addressable