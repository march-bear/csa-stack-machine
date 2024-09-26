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
    def __init__(self, line_number, name: str) -> None:
        super().__init__(f"line {line_number} cannot be interpreted as a {name}")


class ArgumentsError(Exception):
    def __init__(self, line_number: int) -> None:
        super().__init__(f"line {line_number}: invalid argument format")
