class EmptyLabelError(Exception):
    def __init__(self, line_number: int) -> None:
        super().__init__(f"line {line_number}: label doesn't indicate anything")


class SecondLabelDeclarationError(Exception):
    def __init__(self, line_number: int) -> None:
        super().__init__(f"line {line_number}: second label declaration")


class LabelIsNotExistError(Exception):
    def __init__(self, label_name, tag: str) -> None:
        super().__init__(f"{tag} label {label_name} is not exist")


class EmptySectionError(Exception):
    def __init__(self, line_num: int, tag: str) -> None:
        super().__init__(f"line {line_num}: section {tag} doesn't contain any data")


class NoSectionCodeError(Exception):
    def __init__(self) -> None:
        super().__init__(f"there is section .data, but not section .code")

class InterpretationError(Exception):
    def __init__(self, line_number, line, obj: str) -> None:
        self.message = f"line {line_number} cannot be interpreted as a {obj}:\n{line}"
        super().__init__(self.message)


class ArgumentsError(Exception):
    def __init__(self, line_number: int) -> None:
        super().__init__(f"line {line_number}: invalid argument format")


class StatementArgumentError(Exception):
    def __init__(self, line_number, stat) -> None:
        self.message = f"line {line_number}: wrong argument format for statement '{stat}'"
        super().__init__(self.message)


class UnknownCommandError(Exception):
    def __init__(self, line_number, command_name) -> None:
        self.message = f"line {line_number}: unknown command: {command_name}"
        super().__init__(self.message)
