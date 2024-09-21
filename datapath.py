from memory import Memory
from stack import Stack
from sels import AluOpSel, TosInSel, LAluSel, RAluSel, AluModSel


DATA_MEM_SIZE = 64
STACK_SIZE = 64


class Datapath:
    data_mem: Memory = None
    stack: Stack = None

    AR = None
    TOS = None

    input_buf: list = None
    output_buf: list = None

    alu_value = None
    arg_value = None


    def __init__(self, data, input_buf: list) -> None:
        self.data_mem = Memory(data, DATA_MEM_SIZE)
        self.stack = Stack(STACK_SIZE)

        self.AR = 0
        self.TOS = 0

        self.input_buf = input_buf.copy()

        self.alu_value = 0
        self.arg_value = 0


    def alu(self, lsel: LAluSel, rsel: RAluSel, opsel: AluOpSel = AluOpSel.PLUS, modsel: AluModSel = AluModSel.NONE):
        left = self.stack.peek() if (lsel == LAluSel.STACK) else 0
        right = self.TOS if (rsel == RAluSel.TOS) else 0

        res = left + right if (opsel == AluOpSel.PLUS) else left - right

        return res % 2 if (modsel == AluModSel.MOD2) else res
    

    def latch_tos(self, sel: TosInSel):
        match sel:
            case TosInSel.ARG:
                self.TOS = self.arg_value
            case TosInSel.MEM:
                self.TOS = self.mem_oe()
            case TosInSel.ALU:
                self.TOS = self.alu_value
            case TosInSel.INPUT:
                assert len(self.input_buf) > 0, "input is empty"

                self.TOS = self.input_buf.pop()


    def mem_oe(self):
        return self.data_mem.read(self.AR)
    

    def mem_wr(self) -> None:
        self.data_mem[self.AR] = self.alu_value


    def latch_ar(self):
        assert 0 <= self.alu_value < DATA_MEM_SIZE, f"out of memory: {self.alu_value}"

        self.AR = self.alu_value


    def pop_stack(self) -> None:
        self.stack.pop()


    def push_stack(self) -> None:
        self.stack.push(self.alu_value)

    
    def is_tos_zero(self):
        return self.TOS == 0
    

    def is_tos_neg(self):
        return self.TOS < 0
    

    def output(self) -> None:
        self.output_buf.append(self.alu_value)
