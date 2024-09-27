import json
import logging
import sys

from controlunit import ControlUnit
from datapath import Datapath


def simulation(program: list, input_tokens: list = []) -> tuple[list, int, int]:
    if len(program) > 1 and isinstance(program[0], list):
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
        instr_counter += 1
        if all(0 <= token < 0x110000 for token in dp.output_buf):
            pass
            logging.info(f"output_buffer (string): {''.join([chr(token) for token in dp.output_buf])}")
        else:
            pass
            logging.warning("output_buffer (string): UNREADABLE")

        logging.info(f"output_buffer (values): {dp.output_buf}")
    except Exception:
        logging.exception("Found an error")
        return [], 0, 0

    ticks = cu._tick

    return dp.output_buf.copy(), instr_counter, ticks


def main(target, input_stream) -> None:
    program_file = target
    input_file = input_stream
    with open(program_file) as pfile:
        program_json = pfile.read()

    program = json.loads(program_json)

    input_tokens = []
    if input_file is not None:
        with open(input_file) as ifile:
            input_tokens = ifile.read()

    output_buf, instr_counter, ticks = simulation(program, [ord(ch) for ch in input_tokens])
    if all(0 <= token < 0x110000 for token in output_buf):
        print("output:", "".join([chr(token) for token in output_buf]))
    else:
        print("output:", *output_buf)
    print(f"instr_counter: {instr_counter} ticks: {ticks}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    args = sys.argv
    if (len(args)) not in (2, 3):
        logging.error("expected args: program_file [input_file]")
        sys.exit(1)

    program_file = args[1]
    input_file = args[2] if (len(args) == 3) else None

    main(program_file, input_file)
