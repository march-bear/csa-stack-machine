import logging

from memory import Memory, Stack
from sels import AluModSel, AluOpSel, LAluSel, RAluSel, TosInSel


DATA_MEM_SIZE = 64
STACK_SIZE = 64
MACHINE_WORD_MASK = 0xFFFFFFFF
MACHINE_WORD_MAX_POS = 0x7FFFFFFF


class Datapath:
    data_mem: Memory = None
    stack: Stack = None

    AR = None
    BR = None
    TOS = None

    input_buf: list = None
    output_buf: list = None

    alu_value = None
    arg_value = None

    def __init__(self, data: list = [], input_buf: list = []) -> None:
        self.data_mem = Memory(data, DATA_MEM_SIZE)
        self.stack = Stack(STACK_SIZE)

        self.AR = 0
        self.TOS = 0
        self.BR = 0

        self.input_buf = input_buf.copy()
        self.output_buf = []

        self.alu_value = 0
        self.arg_value = 0

    def alu(self, lsel: LAluSel, rsel: RAluSel, opsel: AluOpSel = AluOpSel.PLUS, modsel: AluModSel = AluModSel.NONE):
        left = self.stack.peek() if (lsel == LAluSel.STACK) else 0
        right = self.TOS if (rsel == RAluSel.TOS) else 0

        res = (left + right if (opsel == AluOpSel.PLUS) else left - right) & MACHINE_WORD_MASK
        if res > MACHINE_WORD_MAX_POS:
            res -= MACHINE_WORD_MASK + 1

        self.alu_value = res % 2 if (modsel == AluModSel.MOD2) else res

    def latch_tos(self, sel: TosInSel) -> None:
        match sel:
            case TosInSel.ARG:
                self.TOS = self.arg_value
            case TosInSel.MEM:
                self.TOS = self.mem_oe()
            case TosInSel.ALU:
                self.TOS = self.alu_value
            case TosInSel.BR:
                self.TOS = self.BR
            case TosInSel.INPUT:
                if (len(self.input_buf)) > 0:
                    self.TOS = self.input_buf.pop(0)
                    logging.debug("input: %s", repr(self.TOS))
                else:
                    self.TOS = 0
                    logging.warning("input: EMPTY!")

    def latch_br(self) -> None:
        self.BR = self.stack.peek()

    def mem_oe(self) -> int:
        return self.data_mem.read(self.AR)

    def mem_wr(self) -> None:
        self.data_mem.write(self.AR, self.alu_value)

    def latch_ar(self) -> None:
        assert 0 <= self.alu_value < DATA_MEM_SIZE, f"out of memory: {self.alu_value}"

        self.AR = self.alu_value

    def pop_stack(self) -> None:
        self.stack.pop()

    def push_stack(self) -> None:
        self.stack.push(self.alu_value)

    def is_tos_zero(self) -> bool:
        return self.TOS == 0

    def is_tos_neg(self) -> bool:
        return self.TOS < 0

    def output(self) -> None:
        if len(self.output_buf) < 8:
            logging.debug("output: %s << %s", str(self.output_buf), repr(self.alu_value))
        else:
            output = "[..." + (", ".join([v for v in map(str, self.output_buf[-8:])])) + "]"
            logging.debug("output: %s << %s", output, repr(self.alu_value))

        self.output_buf.append(self.alu_value)
