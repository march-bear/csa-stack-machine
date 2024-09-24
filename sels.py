from enum import Enum


class AluOpSel(Enum):
    PLUS = 0
    MINUS = 1


class TosInSel(Enum):
    ARG = 0
    MEM = 1
    ALU = 2
    INPUT = 3
    BR = 4


class LAluSel(Enum):
    ZERO = 0
    STACK = 1


class RAluSel(Enum):
    ZERO = 0
    TOS = 1
    

class AluModSel(Enum):
    NONE = 0
    MOD2 = 1