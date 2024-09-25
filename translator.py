import re
import sys
import json
from isa import Opcode
from errors import *

MACHINE_WORD_MASK = 0xFFFFFFFF 
MACHINE_WORD_MAX_POS = 0x0FFFFFFF

LABEL_PATTERN = r"[a-zA-Z_][a-zA-Z0-9_]*:"
LABEL_NAME_PATTERN = r"[a-zA-Z_][a-zA-Z0-9_]*"
COMMAND_LINE_PATTERN = r"[a-zA-Z][a-zA-Z0-9_]*(?: +\w+)?"
WORD_LINE_PATTERN = r"word(?: +.+)"
BUF_LINE_PATTERN = r"buf(?: +\-?(?:0|[1-9][0-9]*))"
INTEGER_PATTERN = r"\-?(?:0|[1-9][0-9]*)"
STRING_DEFINITION_PATTERN = r"\-?(?:0|[1-9][0-9]*), *(?:\'[^\']*\'|\"[^\"]*\")"


def translate_data_section(lines: list, first_line: int = 1):
    data = []
    labels = {}
    undef_label = None

    for line_num, line in enumerate(lines[first_line:], start=first_line + 1):
        token = line.strip()

        if token == '':
            pass
        elif token == "section .code":
            assert len(data) > 0, f"section .data doesn't contain any data"
            break
        elif re.fullmatch(LABEL_PATTERN, token):
            if undef_label is not None:
                raise EmptyLabelException(undef_label['line'], undef_label['name'])

            label_name = token.rstrip(':')
            if label_name in labels.keys():
                raise SecondLabelDeclarationException(line_num, label_name)

            undef_label = {"name": label_name, "line": line_num, "addr": len(data)}
        elif re.fullmatch(WORD_LINE_PATTERN, token, flags=re.IGNORECASE):
            args_line = token.split(maxsplit=1)[1]
            if re.fullmatch(INTEGER_PATTERN, args_line):
                data.append(int(args_line))
            elif re.fullmatch(STRING_DEFINITION_PATTERN, args_line):
                length, _string = args_line.split(", ", maxsplit=1)
                string = _string.strip()[1:-1]

                data.append(int(length))
                [data.append(ord(ch)) for ch in string]
            else: 
                raise StatementArgumentException(line_num, "word")

            if undef_label is not None:
                labels[undef_label["name"]] = undef_label["addr"]
                undef_label = None
        elif re.fullmatch(BUF_LINE_PATTERN, token, flags=re.IGNORECASE):
            arg = int(token.split(maxsplit=1)[1])
            assert arg > 0, f"line {line_num}: buf size can't be negative or 0"
            [data.append(0) for _ in range(arg)]

            if undef_label is not None:
                labels[undef_label["name"]] = undef_label["addr"]
                undef_label = None
        else:
            raise InterpretationException(line_num, line, "data line")

    if undef_label is not None:
        raise EmptyLabelException(undef_label["line"], undef_label["name"])

    return data, line_num - 1, labels


def translate_code_section(lines: list, first_line: int = 0):
    result = []
    labels = {}
    undef_label = None

    instr_counter = 0
    for line_num, line in enumerate(lines[first_line:], start=first_line + 1):
        lstrip_line = line.lstrip()
        char_number = len(line) - len(lstrip_line)
        token = lstrip_line.rstrip()

        if token == '':
            pass
        elif re.fullmatch(LABEL_PATTERN, token):
            if undef_label is not None:
                raise EmptyLabelException(undef_label['line'], undef_label['name'])

            label_name = token.rstrip(':')
            if label_name in labels.keys():
                raise SecondLabelDeclarationException(line_num, label_name)

            undef_label = {"name": label_name, "line": line_num}
        elif re.fullmatch(COMMAND_LINE_PATTERN, token):
            args_line = None
            if len(_splited_token := token.split(maxsplit=1)) == 1:
                command = _splited_token[0]
            else:
                command, args_line = _splited_token

            arg = None
            match command := command.lower():
                case (
                    Opcode.DUP 
                    | Opcode.ADD 
                    | Opcode.DEC 
                    | Opcode.SWAP 
                    | Opcode.MOD2 
                    | Opcode.PRINT 
                    | Opcode.INPUT 
                    | Opcode.PUSH_BY 
                    | Opcode.POP_BY 
                    | Opcode.DEL_TOS 
                    | Opcode.HALT
                ):
                    if args_line is not None:
                        raise ArgumentsException(line_num, line, command)

                case Opcode.JMP | Opcode.JZ | Opcode.JG:
                    if args_line is None or not re.fullmatch(LABEL_NAME_PATTERN, args_line):
                        raise ArgumentsException(line_num, line, command, ["label_name"])

                    arg = args_line
                case Opcode.PUSH:
                    if args_line is None: args_line = ''

                    if re.fullmatch(INTEGER_PATTERN, args_line):
                        arg = int(args_line)
                    elif re.fullmatch(LABEL_NAME_PATTERN, args_line):
                        arg = args_line
                    else:
                        raise ArgumentsException(line_num, line, command, ["integer, label_name"])
                case Opcode.POP:
                    if args_line is None: args_line = ''

                    if re.fullmatch(LABEL_NAME_PATTERN, args_line):
                        arg = args_line
                    else:
                        raise ArgumentsException(line_num, line, command, ["label_name"])
                case _:
                    raise UnknownCommandException(line_num, command)

            instr_info = {}
            instr_info["opcode"] = command
            if arg is not None: 
                if type(arg) is int: 
                    arg = arg & MACHINE_WORD_MASK
                    if (arg > MACHINE_WORD_MAX_POS): arg -= MACHINE_WORD_MASK + 1
                instr_info["arg"] = arg
            instr_info["term"] = [line_num, char_number, token]

            result.append(instr_info)

            if undef_label != None:
                labels[undef_label["name"]] = {"instr": instr_counter, "line": undef_label["line"]}
                undef_label = None

            instr_counter += 1
        else:
            raise InterpretationException(line_num, line, "code line")

    if undef_label is not None: 
        raise EmptyLabelException(undef_label['line'], undef_label['line'])

    return result, labels


def replace_label_names(code, instr_labels, data_labels):
    if type(code[0] is list):
        first_instr = 1
    else:
        first_instr = 0

    for instr in code[first_instr:]:
        match instr["opcode"]:
            case Opcode.JMP | Opcode.JZ | Opcode.JG:
                if instr["arg"] not in instr_labels.keys():
                    raise LabelIsNotExistException(instr["arg"], "instr")

                instr["arg"] = instr_labels[instr["arg"]]["instr"]
            case Opcode.POP | Opcode.PUSH:
                if type(instr["arg"]) is str:
                    if instr["arg"] not in data_labels.keys():
                        raise LabelIsNotExistException(instr["arg"], "data")

                    instr["arg"] = data_labels[instr["arg"]]


def translate_with_sections(lines: list):
    data_list, cs_line, data_labels = translate_data_section(lines)
    assert cs_line != -1, "found `section .data` but not `section .code`"
    assert len(data_list) > 0, "section .data is empty"

    instr_list, instr_labels = translate_code_section(lines, cs_line + 1)
    assert len(instr_list) > 0, "section .code is empty"

    exec_file_data = [data_list, *instr_list]

    return exec_file_data, instr_labels, data_labels


def translate_without_sections(lines: list):
    code, instr_labels = translate_code_section(lines)
    return code, instr_labels, {}


def translate(program):
    lines = program.rstrip().split("\n")
    if len(lines) == 0:
        return []

    if lines[0].strip() == "section .data":
        code, instr_labels, data_labels = translate_with_sections(lines)
    else:
        code, instr_labels, data_labels = translate_without_sections(lines)

    replace_label_names(code, instr_labels, data_labels)
    return code


def main(code, target):
    try:
        input_file = code
        output_file = target

        with open(input_file, "r") as ifile:
            program = ifile.read()

        code = translate(program)

        buf = []
        for instr in code:
            buf.append(json.dumps(instr))

        with open(output_file, "w") as ofile:
            ofile.write("[" + ",\n ".join(buf) + "]")

        print("LoC:", len(program.split('\n')), "code instr:", len(code))
    except Exception as ex:
        print(f"error: {ex.__class__.__name__}: {ex}\n")


if __name__ == "__main__":
    args = sys.argv
    try:
        assert len(args) in (2, 3), "expected args: input_file_name [output_file_name]"
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
        print(f"error: {ex.__class__.__name__}: {ex}\n")
