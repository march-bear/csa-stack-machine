from enum import Enum

class Opcode(str, Enum):
    DUP = "dup"
    ADD = "add"
    DEC = "dec"
    SWAP = "swap"
    MOD2 = "mod2"
    PRINT = "print"
    INPUT = "input"

    JMP = "jmp"
    JZ = "jz"
    JG = "jg"

    PUSH_BY = "push_by"
    PUSH = "push"
    PUSH_MEM = "push_mem"
    POP = "pop"

    HALT = "halt"

    def __str__(self):
        return str(self.value)