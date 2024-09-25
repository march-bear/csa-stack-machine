import sys
import json
import logging
from datapath import Datapath
from controlunit import ControlUnit


DONE_EXIT_CODE = 0
WRONG_SYS_ARGV_EXIT_CODE = 1
SIMULATION_ERROR_EXIT_CODE = 2


def simulation(program, input_tokens: list = []):
    if (len(program) > 1 and type(program[0]) is list):
        data = program[0]
        code = program[1:]
    else:
        data = []
        code = program

    dp = Datapath(data, input_tokens)
    cu = ControlUnit(dp, code)

    try:
        while (True): 
            logging.debug(cu)
            cu.decode_and_execute_instruction()
    except StopIteration:
        if (all(0 <= token < 0x110000 for token in dp.output_buf)):
            logging.info(f"output_buffer: {''.join([chr(token) for token in dp.output_buf])}")
        else:
            logging.warning(f"output UNREADABLE")
            logging.info(f"output_buffer (values): {dp.output_buf}")
    except Exception as ex:
        logging.error(f"{ex.__class__.__name__}: {ex}")
        return SIMULATION_ERROR_EXIT_CODE
    
    return DONE_EXIT_CODE


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
    if (input_file is not None):
        with open(input_file, "r") as ifile:
            input_tokens_json = ifile.read()
    
        input_tokens = json.loads(input_tokens_json)

    exit_code = simulation(program, input_tokens)
    sys.exit(exit_code)