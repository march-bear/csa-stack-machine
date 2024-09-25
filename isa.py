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
    POP_BY = "pop_by"
    POP = "pop"
    DEL_TOS = "del_tos"

    HALT = "halt"

    def __str__(self):
        return str(self.value)