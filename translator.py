import re
import sys
import json
from isa import Opcode


LABEL_PATTERN = r'[a-zA-Z_][a-zA-Z0-9_]*:'
LABEL_NAME_PATTERN = r'[a-zA-Z_][a-zA-Z0-9_]*'
COMMAND_LINE_PATTERN = r'[a-zA-Z][a-zA-Z0-9_]*(?: +\w+)?'
WORD_LINE_PATTERN = r'word(?: +.+)'
BUF_LINE_PATTERN = r''
INTEGER_PATTERN = r'\-?(?:0|[1-9][0-9]*)'
STRING_DEFINITION_PATTERN = r'\-?(?:0|[1-9][0-9]*), *(?:\'[^\']*\'|\"[^\"]*\")'


def translate_data_section(lines: list, first_line: int = 1):
    data = []
    labels = {}
    last_undefined_label_info = None
    

    for line_number, line in enumerate(lines[first_line:], start=first_line):
        token = line.strip()

        if (token == ''):
            pass
        elif (token == "section .code"):
            assert len(data) > 0, f"section .data doesn't contain any data"
            break
        elif (re.fullmatch(LABEL_PATTERN, token)):
            assert last_undefined_label_info is None, f"line {last_undefined_label_info['line']}: label {last_undefined_label_info['name']} does not indicate data"
            label_name = token.rstrip(':')
            assert label_name not in labels.keys(), f"line {line_number}: second label declaration {label_name}"

            last_undefined_label_info = {"name": label_name, "line": line_number, "addr": len(data)}
        elif (re.fullmatch(WORD_LINE_PATTERN, token, flags=re.IGNORECASE)):
            args_line = token.split(maxsplit=1)[1]
            if (re.fullmatch(INTEGER_PATTERN, args_line)):
                data.append(int(args_line))
            elif (re.fullmatch(STRING_DEFINITION_PATTERN, args_line)):
                length, _string = args_line.split(", ", maxsplit=1)
                string = _string.strip()[1:-1]

                data.append(int(length))
                [data.append(ord(ch)) for ch in string]
            else: 
                raise Exception(f"line {line_number}: wrong argument format for statement 'word'")

            if (last_undefined_label_info is not None):
                labels[last_undefined_label_info["name"]] = last_undefined_label_info["addr"]
                last_undefined_label_info = None

        else:
            raise Exception(f"line {line_number} cannot be interpreted as a data line:\n{line}")
    
    assert last_undefined_label_info is None, \
        f"line {last_undefined_label_info['line']}: label {last_undefined_label_info['name']} does not indicate data"
    
    return data, line_number, labels


def translate_code_section(lines: list, first_line: int = 0, data_labels: dict = {}):
    result = []
    instr_labels = {}
    last_undefined_instr_label_info = None
    
    instr_counter = 0
    for line_number, line in enumerate(lines[first_line:], start=first_line):
        lstrip_line = line.lstrip()
        char_number = len(line) - len(lstrip_line)
        token = lstrip_line.rstrip()

        if (token == ''):
            pass
        elif (re.fullmatch(LABEL_PATTERN, token)):
            assert last_undefined_instr_label_info is None, \
                f"line {last_undefined_instr_label_info['line']}: label {last_undefined_instr_label_info['name']} does not indicate instructions"
            
            label_name = token.rstrip(':')
            assert label_name not in instr_labels.keys(), f"line {line_number}: second label declaration {label_name}"

            last_undefined_instr_label_info = {"name": label_name, "line": line_number}
        elif (re.fullmatch(COMMAND_LINE_PATTERN, token)):
            args_line = None
            if (len(_splited_token := token.split(maxsplit=1)) == 1):
                command = _splited_token[0]
            else:
                command, args_line = _splited_token
            
            arg = None
            match (command := command.lower()):
                case Opcode.DUP | Opcode.ADD | Opcode.DEC | Opcode.MOD2 | Opcode.PRINT | Opcode.INPUT | Opcode.PUSH_BY | Opcode.HALT:
                    assert args_line is None, f"line {line_number}: command {command} doesn't require any arguments:\n {line}"
                case Opcode.JMP | Opcode.JZ | Opcode.JG:
                    assert args_line is not None and re.fullmatch(LABEL_NAME_PATTERN, args_line), \
                        f"line {line_number}: command {command} takes one argument: label name:\n {line}"
                    arg = args_line
                case Opcode.PUSH:
                    assert args_line is not None, f"line {line_number}: command {command} takes one argument in format integer_number or label_name:\n{line}"
                    if (re.fullmatch(INTEGER_PATTERN, args_line)):
                        arg = int(args_line)
                    elif (re.fullmatch(LABEL_NAME_PATTERN, args_line)):
                        if ((label_name := args_line) in data_labels.keys()):
                            arg = data_labels[label_name]
                            # TODO
                    else:
                        raise Exception(f"line {line_number}: command {command} takes one argument in format integer_number or label_name:\n{line}")
                case Opcode.POP:
                    assert args_line is not None, f"line {line_number}: command {command} takes one argument: label_name:\n{line}"
                    if (re.fullmatch(LABEL_NAME_PATTERN, args_line)):
                        if ((label_name := args_line) in data_labels.keys()):
                            arg = data_labels[label_name]
                            # TODO
                    else:
                        raise Exception(f"line {line_number}: command {command} takes one argument in format integer_number or label_name:\n{line}")
                case _:
                    raise Exception(token)
                    
            result.append({"opcode": command, "term": [line_number, char_number, token]})
            if (arg is not None):
                result[-1]["arg"] = arg

            if (last_undefined_instr_label_info != None):
                instr_labels[last_undefined_instr_label_info["name"]] = {"instr": instr_counter}
                last_undefined_instr_label_info = None
            
            instr_counter += 1
        else:
            raise Exception(f"line {line_number} cannot be interpreted as a code line:\n{line}")
    
    assert last_undefined_instr_label_info is None, \
        f"line {last_undefined_instr_label_info['line']}: label {last_undefined_instr_label_info['name']} does not indicate instructions"
    
    for instr in result:
        if (instr["opcode"] in (Opcode.JMP, Opcode.JZ, Opcode.JG)):
            instr["arg"] = instr_labels[instr["arg"]]["instr"]

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
    args = sys.argv
    try:
        assert len(args) in (2, 3), "expented args: input_file_name [output_file_name]"
        input_file = args[1]
        output_file = args[2] if (len(args) == 3) else input_file + ".out"

        print(f"input file: {input_file}")
        print(f"output file: {output_file}")
        print()

        with open(input_file, "r") as ifile:
            program = ifile.read()

        code = translate(program)

        buf = []
        for instr in code:
            buf.append(json.dumps(instr))

        with open(output_file, "w") as ofile:
            ofile.write("[" + ",\n ".join(buf) + "]")

        print("translation is succesful")
    except Exception as ex:
        print(f"error: {ex}\n")
        
