from datapath import Datapath
from memory import Memory
from isa import Opcode
from sels import LAluSel, RAluSel, AluOpSel, TosInSel


INSTR_MEM_SIZE = 64


class ControlUnit:
    dp: Datapath = None
    instr_mem: Memory = None

    # IA - instr_argument
    # IP - instr_pointer
    IA = None
    IP = None


    def __init__(self, dp: Datapath, data: list) -> None:
        self.dp = dp
        self.instr_mem = Memory(data, INSTR_MEM_SIZE)


    def decode_and_execute_instruction(self):
        instr = self.instr_mem.read(self.IP)
        opcode = instr["opcode"]

        match opcode:
            case Opcode.DUP:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
            case Opcode.ADD:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.PLUS)

                self.dp.pop_stack()
            case Opcode.DEC:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.MINUS)

                self.dp.pop_stack()
            case Opcode.PUSH:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()

                self.dp.arg_value = self.IA
                self.dp.latch_tos(TosInSel.ARG)

                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.latch_ar()

                self.dp.latch_tos(TosInSel.MEM)
            case Opcode.POP:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()

                self.dp.arg_value = self.IA
                self.dp.latch_tos(TosInSel.ARG)

                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.latch_ar()

                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.mem_wr()

                self.dp.pop_stack()

                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.latch_tos(TosInSel.ALU)

                self.dp.pop_stack()
            case Opcode.PRINT:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS, AluOpSel.PLUS)
                self.dp.output()
        

