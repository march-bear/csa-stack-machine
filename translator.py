import json
import re
import sys

from errors import (
    ArgumentsError,
    EmptyLabelError,
    EmptySectionError,
    InterpretationError,
    LabelIsNotExistError,
    NoSectionCodeError,
    SecondLabelDeclarationError,
)
from isa import Opcode

MACHINE_WORD_MASK = 0xFFFFFFFF
MACHINE_WORD_MAX_POS = 0x0FFFFFFF

LABEL_PATTERN = r"[a-zA-Z_][a-zA-Z0-9_]*:"
LABEL_NAME_PATTERN = r"[a-zA-Z_][a-zA-Z0-9_]*"
COMMAND_LINE_PATTERN = r"[a-zA-Z][a-zA-Z0-9_]*(?: +\w+)?"
WORD_LINE_PATTERN = r"word(?: +.+)"
BUF_LINE_PATTERN = r"buf(?: +\-?(?:0|[1-9][0-9]*))"
INTEGER_PATTERN = r"\-?(?:0|[1-9][0-9]*)"
STRING_DEFINITION_PATTERN = r"\-?(?:0|[1-9][0-9]*), *(?:\'[^\']*\'|\"[^\"]*\")"


def raise_if_not(sel, err):
    if (sel):
        raise err


def token_to_dict(token: str):
    _list = token.split(maxsplit=1)

    match len(_list):
        case 0:
            return {}
        case 1:
            if re.fullmatch(LABEL_PATTERN, _list[0]):
                return {"statement": _list[0].rstrip(":"), "args": [], "is_label": True, "err": False}
            else:
                return {"statement": _list[0], "is_label": False, "err": False}
        case _:
            args_str = _list[1]
            args = []
            while (args_str != ""):
                integer = re.match(INTEGER_PATTERN, args_str)
                string = re.match(STRING_DEFINITION_PATTERN, args_str)
                label_name = re.match(LABEL_NAME_PATTERN)

                if (integer is not None):
                    start = integer.start()
                    end = integer.end()

                    arg = int(args_str[start:end])  & MACHINE_WORD_MASK
                    if arg > MACHINE_WORD_MAX_POS:
                        arg -= MACHINE_WORD_MASK + 1

                    args.append()
                elif (string is not None):
                    start = string.start()
                    end = string.end()

                    string_def = args_str[start:end]
                    arg = string_def.strip('"') if string_def[0] == '"' else string_def.strip("'")
                    args.append(arg)
                elif (label_name is not None):
                    start = label_name.start()
                    end = label_name.end()

                    arg = args_str[start:end]
                    args.append(tuple([arg]))
                else:
                    return {"err": True}

                args_str = args_str[end:]
                if (args_str != "" and args_str[0] != ","):
                    return {"err": True}
                
                args_str = args_str[1:].lstrip()

            return {"statement": _list[0], "args": args, "is_label": False, "err": False}


def translate_data_section(lines: list, first_line: int = 1):
    data = []
    labels = {}
    undef_label = {"name": None, "line": None, "addr": None}

    for line_num, line in enumerate(lines[first_line:], start=first_line + 1):
        token = line.strip()

        if (token == "section .code"):
            raise_if_not(len(data) > 0, EmptySectionError(line_num - 1, ".data"))
            return data, line_num - 1, labels

        token_dict = token_to_dict()

        if (len(token_dict) == 0):
            continue

        raise_if_not(not token_dict["err"], ArgumentsError(line_num))
        
        if (token_dict["is_label"]):
            label_name = token_dict["statement"]
            raise_if_not(label_name not in labels.keys(), SecondLabelDeclarationError(line_num))
            raise_if_not(undef_label["name"] == None, EmptyLabelError(undef_label["line"]))

            undef_label["name"] = label_name
            undef_label["addr"] = len(data)
            undef_label["line"] = line_num
            continue

        match token_dict["statement"].lower():
            case "":
                continue
            case "word":
                raise_if_not(len(token_dict["args"]) == 2, ArgumentsError(line_num))
                length = token_dict["args"][0]
                string = token_dict["args"][1]
                raise_if_not(isinstance(length, int) and isinstance(string, str), ArgumentsError(line_num))
                raise_if_not(length == len(string) and length != 0, ArgumentsError(line_num))

                data.append(length)
                data.append(ord(ch) for ch in string)
            case "buf":
                raise_if_not(len(token_dict["args"]) == 1, ArgumentsError(line_num))
                arg = token_dict["args"][0]
                raise_if_not(isinstance(arg, int), ArgumentsError(line_num))
                raise_if_not(arg > 0)

                data.append(0 for _ in range(arg))

        if (undef_label["name"] is not None):
            labels["name"] = undef_label["addr"]
            undef_label["name"] = None
    
    raise NoSectionCodeError()


def translate_code_section(lines: list, first_line: int = 0):
    instrs = []
    labels = {}
    undef_label = {"name": None, "addr": None, "line": None}

    for line_num, line in enumerate(lines[first_line:], start=first_line + 1):
        lstrip_line = line.lstrip()
        token = lstrip_line.rstrip()
        token_dict = token_to_dict(token)

        raise_if_not(not token_dict["err"], ArgumentsError(line_num))
        
        if (token_dict["is_label"]):
            label_name = token_dict["statement"]
            raise_if_not(label_name not in labels.keys(), SecondLabelDeclarationError(line_num))
            raise_if_not(undef_label["name"] == None, EmptyLabelError(undef_label["line"]))

            undef_label["name"] = label_name
            undef_label["addr"] = len(len(instrs))
            undef_label["line"] = line_num
            continue

        opcode = token_dict["statement"].lower()
        term = [line_num, len(line) - len(lstrip_line), token]
        
        match opcode:
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
                raise_if_not(len(token_dict["args"]) == 0, ArgumentsError(line_num))
                instrs.append({"opcode": opcode, "term": term})
            case Opcode.JMP | Opcode.JZ | Opcode.JG:
                raise_if_not(len(token_dict["args"]) == 1, ArgumentsError(line_num))
                arg = token_dict["args"][0]
                raise_if_not(isinstance(arg, tuple), ArgumentsError(line_num))
                label = arg[0]
                instrs.append({"opcode": opcode, "arg": label, "term": term})
            case Opcode.PUSH:
                raise_if_not(len(token_dict["args"]) == 1, ArgumentsError(line_num))
                _arg = token_dict["args"][0]
                if (isinstance(_arg, tuple)):
                    arg = _arg[0]
                elif (isinstance(_arg, int)):
                    arg = _arg
                else:
                    raise ArgumentsError(line_num)
                
                instrs.append({"opcode": opcode, "arg": arg, "term": term})
            case Opcode.POP:
                raise_if_not(len(token_dict["args"]) == 1, ArgumentsError(line_num))
                _arg = token_dict["args"][0]
                raise_if_not(isinstance(arg, tuple), ArgumentsError(line_num))
                
                instrs.append({"opcode": opcode, "arg": _arg[0], "term": term})
            case _:
                raise InterpretationError(line_num, "code_line")

    raise_if_not(len(instr) > 0, EmptySectionError(line_num, ".code"))
    raise_if_not(undef_label["name"] is None, EmptyLabelError(undef_label["line"]))
        
    return instrs, labels


def replace_label_names(code, instr_labels, data_labels):
    if isinstance(code[0], list):
        first_instr = 1
    else:
        first_instr = 0

    for instr in code[first_instr:]:
        match instr["opcode"]:
            case Opcode.JMP | Opcode.JZ | Opcode.JG:
                if instr["arg"] not in instr_labels.keys():
                    raise LabelIsNotExistError(instr["arg"], "instr")

                instr["arg"] = instr_labels[instr["arg"]]["instr"]
            case Opcode.POP | Opcode.PUSH:
                if isinstance(instr["arg"], str):
                    if instr["arg"] not in data_labels.keys():
                        raise LabelIsNotExistError(instr["arg"], "data")

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

        with open(input_file) as ifile:
            program = ifile.read()

        code = translate(program)

        buf = []
        for instr in code:
            buf.append(json.dumps(instr))

        with open(output_file, "w") as ofile:
            ofile.write("[" + ",\n ".join(buf) + "]")

        print("LoC:", len(program.split("\n")), "code instr:", len(code))
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

        with open(input_file) as ifile:
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
