MACHINE_WORD_MASK = 0xFFFFFFFF


def translate_data_section(lines: list, first_line: int = 1):
    return [], -1, []


def translate_code_section(lines: list, first_line: int = 0, data_labels: list = []):
    return []


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
