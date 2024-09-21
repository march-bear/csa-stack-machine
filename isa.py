from enum import Enum

class Opcode(str, Enum):
    DUP = "dup"
    ADD = "add"
    DEC = "dec"
    MOD2 = "mod2"
    PRINT = "print"
    INPUT = "input"

    JMP = "jmp"
    JZ = "jz"
    JG = "jg"

    PUSH = "push"
    POP = "pop"

    HALT = "halt"

    def __str__(self):
        return str(self.value)