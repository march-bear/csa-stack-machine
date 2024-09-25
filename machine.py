import sys
import json
import logging
from datapath import Datapath
from controlunit import ControlUnit


DONE_EXIT_CODE = 0
WRONG_SYS_ARGV_EXIT_CODE = 1
SIMULATION_ERROR_EXIT_CODE = 2


def simulation(program, input_tokens: list = []):
    if len(program) > 1 and type(program[0]) is list:
        data = program[0]
        code = program[1:]
    else:
        data = []
        code = program

    dp = Datapath(data, input_tokens)
    cu = ControlUnit(dp, code)
    logging.debug("%s", cu)
    instr_counter = 0
    try:
        while True:
            cu.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", cu)
    except StopIteration:
        logging.info("Simulation ended!")
        if all(0 <= token < 0x110000 for token in dp.output_buf):
            pass
            logging.info(f"output_buffer (string): {''.join([chr(token) for token in dp.output_buf])}")
        else:
            pass
            logging.warning(f"output_buffer (string): UNREADABLE")

        logging.info(f"output_buffer (values): {dp.output_buf}")
    except Exception as ex:
        logging.error(f"{ex.__class__.__name__}: {ex}")
        return SIMULATION_ERROR_EXIT_CODE, None

    ticks = cu._tick

    return DONE_EXIT_CODE, dp.output_buf.copy(), instr_counter, ticks


def main(target, input_stream) -> None:
    program_file = target
    input_file = input_stream
    with open(program_file, "r") as pfile:
        program_json = pfile.read()

    program = json.loads(program_json)

    input_tokens = []
    if (input_file is not None):
        with open(input_file, "r") as ifile:
            input_tokens = ifile.read()

    _, output_buf, instr_counter, ticks = simulation(program, [ord(ch) for ch in input_tokens])
    if all(0 <= token < 0x110000 for token in output_buf):
        print("output:", ''.join([chr(token) for token in output_buf]))
    else:
        print(f"UNREADABLE output: {output_buf}")
    print(f"instr_counter: {instr_counter} ticks: {ticks}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    args = sys.argv
    if (len(args)) not in (2, 3):
        logging.error(f"expected args: program_file [input_file]")
        sys.exit(WRONG_SYS_ARGV_EXIT_CODE)

    program_file = args[1]
    input_file = args[2] if (len(args) == 3) else None

    with open(program_file, "r") as pfile:
        program_json = pfile.read()

    program = json.loads(program_json)

    input_tokens = []
    if input_file is not None:
        with open(input_file, "r") as ifile:
            input_tokens = ifile.read()

    exit_code, _ = simulation(program, [ord(ch) for ch in input_tokens])

    sys.exit(exit_code)
