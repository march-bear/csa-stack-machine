class EmptyLabelError(Exception):
    def __init__(self, line_number, label_name) -> None:
        self.message = f"line {line_number}: label {label_name} doesn't indicate anything"
        super().__init__(self.message)


class SecondLabelDeclarationError(Exception):
    def __init__(self, line_number, label_name) -> None:
        self.message = f"line {line_number}: second label declaration {label_name}"
        super().__init__(self.message)


class LabelIsNotExistError(Exception):
    def __init__(self, label_name, tag: str) -> None:
        self.message = f"{tag} label {label_name} is not exist"
        super().__init__(self.message)


class InterpretationError(Exception):
    def __init__(self, line_number, line, obj: str) -> None:
        self.message = f"line {line_number} cannot be interpreted as a {obj}:\n{line}"
        super().__init__(self.message)


class ArgumentsError(Exception):
    def __init__(self, line_number, line, command_name, formats: list = []) -> None:
        if len(formats) == 0:
            self.message = f"line {line_number}: command {command_name} doesn't require any arguments:\n {line}"
        else:
            self.message = f"line {line_number}: command {command_name} takes 1 argument in format {', or'.join(['<' + str(form) + '>' for form in formats])}:\n{line}"
        super().__init__(self.message)


class StatementArgumentError(Exception):
    def __init__(self, line_number, stat) -> None:
        self.message = f"line {line_number}: wrong argument format for statement '{stat}'"
        super().__init__(self.message)


class UnknownCommandError(Exception):
    def __init__(self, line_number, command_name) -> None:
        self.message = f"line {line_number}: unknown command: {command_name}"
        super().__init__(self.message)
