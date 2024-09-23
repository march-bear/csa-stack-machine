import re
from isa import Opcode

MACHINE_WORD_MASK =     0xFFFFFFFF 
MACHINE_WORD_MAX_POS =  0x0FFFFFFF

LABEL_PATTERN = r'[a-zA-Z_][a-zA-Z0-9_]*:'
COMMAND_LINE_PATTERN = r'[a-zA-Z][a-zA-Z0-9]*(?: +\w+)?'
INTEGER_PATTERN = r'\-?(?:0|[1-9][0-9]*)'


def translate_data_section(lines: list, first_line: int = 1):
    return [], -1, []


def translate_code_section(lines: list, first_line: int = 0, data_labels: list = []):
    result = []
    instr_labels = []
    
    instr_counter = 0
    for line_number, line in enumerate(lines[first_line:]):
        lstrip_line = line.lstrip()
        char_number = len(line) - len(lstrip_line)
        token = line.rstrip()

        if (token == ''):
            pass
        elif (re.fullmatch(LABEL_PATTERN, token)):
            if (len(instr_labels) > 0 and instr_labels[-1]["instr"] == None):
                raise Exception(f"line {instr_labels[-1]["line"]}: label {instr_labels[-1]["name"]} does not indicate instructions")
            
            label_name = token.rstrip(':')
            instr_labels.append({"name": label_name, "instr": None, "line": line_number})
        elif (re.fullmatch(COMMAND_LINE_PATTERN, token)):
            args_line = None
            if (len(_splited_token := token.split(maxsplit=1)) == 1):
                command = _splited_token[0]
            else:
                command, args_line = _splited_token
            
            arg = None
            match (command := command.lower()):
                case Opcode.DUP, Opcode.ADD, Opcode.DEC, Opcode.MOD2, Opcode.PRINT, Opcode.INPUT:
                    assert args_line is None, f"line {line_number}: command {command} doesn't require any arguments:\n {line}"
                case Opcode.JMP, Opcode.JZ, Opcode.JG, Opcode.POP:
                    assert re.fullmatch(LABEL_PATTERN, args_line), f"line {line_number}: command {command} takes one argument: label name:\n {line}"
                    arg = args_line
                case Opcode.PUSH:
                    if (re.fullmatch(INTEGER_PATTERN, args_line)):
                        arg = int(args_line)
                    elif (args_line[0] == '(' and args_line[-1] == ')' and re.fullmatch(LABEL_PATTERN, args_line[1:-1])):
                        label_name = args_line[1:-1]
                        if (data_labels.)
                    else:
                        raise Exception(f"line {line_number}: command {command} takes one argument in format integer_number or (label_name)")
                    
            result.append({"opcode": command, "term": [line_number, char_number, token]})
            if (arg):
                result[-1]["arg"] = arg

            if (len(instr_labels) > 0 and instr_labels[-1]["instr"] == None):
                instr_labels[-1]["instr"] = instr_counter
            
            instr_counter += 1
        else:
            raise Exception(f"line {line_number} cannot be interpreted as a code line:\n{line}")
    
    if (len(instr_labels) > 0 and instr_labels[-1]["instr"] == None):
        raise Exception(f"line {instr_labels[-1]["line"]}: label {instr_labels[-1]["name"]} does not indicate instructions")
    
    return result


def translate_with_sections(lines: list):
    data_list, cs_line, data_labels = translate_data_section(lines)
    assert cs_line != -1, "found `section .data` but not `section .code`"
    assert len(data_list) > 0, "section .data is empty"

    instr_list = translate_code_section(lines, cs_line + 1, data_labels)
    assert len(instr_list) > 0, "section .code is empty"

    exec_file_data = [data_list, *instr_list]

    return exec_file_data


def translate(program):
    lines = program.rstrip().split("\n")
    if (len(lines) == 0):
        return []
    
    if (lines[0].strip() == "section .data"):
        return translate_with_sections(lines)
    else:
        return translate_code_section(lines)


if __name__ == "__main__":
    translate([])
