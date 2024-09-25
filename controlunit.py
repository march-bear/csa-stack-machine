from datapath import Datapath
from isa import Opcode
from sels import AluModSel, AluOpSel, LAluSel, RAluSel, TosInSel


class ControlUnit:
    dp: Datapath = None
    instr_mem: list = None

    # IA - instr_argument
    IA = None
    # IP - instr_pointer
    IP = None

    _tick = None

    def __init__(self, dp: Datapath, code: list) -> None:
        self.IA = 0
        self.IP = 0
        self.dp = dp
        self.instr_mem = code.copy()

        self._tick = 0

    def tick(self) -> None:
        self._tick += 1

    def jump_if(self, sel: bool) -> None:
        if sel:
            assert 0 <= self.IA < len(self.instr_mem), f"out of memory: {self.IA}"
            self.IP = self.IA
        else:
            self.IP += 1
        self.tick()

    def decode_and_execute_instruction(self):
        assert 0 <= self.IP < len(self.instr_mem), f"out of memory: {self.IP}"
        instr = self.instr_mem[self.IP]

        if "arg" in instr.keys():
            self.IA = instr["arg"]
        opcode = instr["opcode"]

        self.tick()

        match opcode:
            case Opcode.HALT:
                raise StopIteration()
            case Opcode.JMP:
                self.jump_if(True)
            case Opcode.JZ:
                self.jump_if(self.dp.is_tos_zero())
            case Opcode.JG:
                self.jump_if(not self.dp.is_tos_neg())
            case _:
                self.IP += 1

        match opcode:
            case Opcode.DUP:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
            case Opcode.ADD:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.PLUS)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.DEC:
                self.dp.alu(LAluSel.STACK, RAluSel.TOS, AluOpSel.MINUS)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.MOD2:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS, modsel=AluModSel.MOD2)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
            case Opcode.SWAP:
                self.dp.latch_br()
                self.tick()
                self.dp.pop_stack()
                self.tick()
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
                self.dp.latch_tos(TosInSel.BR)
                self.tick()
            case Opcode.PUSH_BY:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.latch_ar()
                self.tick()
                self.dp.latch_tos(TosInSel.MEM)
                self.tick()
            case Opcode.PUSH:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.tick()
                self.dp.arg_value = self.IA
                self.dp.latch_tos(TosInSel.ARG)
                self.tick()
            case Opcode.POP_BY:
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
            case Opcode.DEL_TOS:
                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.PRINT:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.output()
                self.tick()
                self.dp.alu(LAluSel.STACK, RAluSel.ZERO)
                self.dp.latch_tos(TosInSel.ALU)
                self.tick()
                self.dp.pop_stack()
                self.tick()
            case Opcode.INPUT:
                self.dp.alu(LAluSel.ZERO, RAluSel.TOS)
                self.dp.push_stack()
                self.dp.latch_tos(TosInSel.INPUT)
                self.tick()

    def __repr__(self):
        return "TICK: {:3} IP: {:3} AR: {:3} MEM_OUT: {:3} INSTR: {:10} TOS: {:3} STACK: {}".format(
            self._tick,
            self.IP,
            self.dp.AR,
            self.dp.mem_oe(),
            f"{self.instr_mem[self.IP]['opcode']} {'' if 'arg' not in self.instr_mem[self.IP].keys() else self.instr_mem[self.IP]['arg']}",
            self.dp.TOS,
            self.dp.stack.data,
        )
