from datapath import Datapath
from memory import Memory
from isa import Opcode
from sels import LAluSel, RAluSel, AluOpSel, TosInSel, AluModSel


INSTR_MEM_SIZE = 64


class ControlUnit:
    dp: Datapath = None
    instr_mem: Memory = None

    # IA - instr_argument
    # IP - instr_pointer
    IA = None
    IP = None

    _tick = None


    def __init__(self, dp: Datapath, data: list) -> None:
        self.dp = dp
        self.instr_mem = Memory(data, INSTR_MEM_SIZE)

        self._tick = 0


    def tick(self) -> None:
        self._tick += 1


    def jump_if(self, sel: bool) -> None:
        if (sel):
            assert 0 <= self.IA < INSTR_MEM_SIZE, f"out of memory: {self.IA}"
            self.IP = self.IA


    def decode_and_execute_instruction(self):
        instr = self.instr_mem.read(self.IP)
        opcode = instr["opcode"]

        match opcode:
            case Opcode.HALT:
                raise StopIteration()
            case Opcode.JMP:
                self.jump_if(True)
                self.tick()
            case Opcode.JZ:
                self.jump_if(self.dp.is_tos_zero)
                self.tick()
            case Opcode.JG:
                self.jump_if(not self.dp.is_tos_neg)
                self.tick()

        match opcode:
            case Opcode.DUP:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
            case Opcode.ADD:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.PLUS)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.DEC:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.MINUS)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.MOD2:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS, modsel=AluModSel.MOD2)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
            case Opcode.PUSH:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
                self.dp.arg_value = self.IA
                self.dp.latch_tos(TosInSel.ARG)
                self.tick()
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.latch_ar()
                self.tick()
                self.dp.latch_tos(TosInSel.MEM)
                self.tick()
            case Opcode.POP:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
                self.dp.arg_value = self.IA
                self.dp.latch_tos(TosInSel.ARG)
                self.tick()
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.latch_ar()
                self.tick()
                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.mem_wr()
                self.tick()
                self.dp.pop_stack()
                self.tick()
                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.PRINT:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS, AluOpSel.PLUS)
                self.dp.output()
                self.tick()
