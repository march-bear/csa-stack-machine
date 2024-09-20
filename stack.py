class Stack:
    size = None
    data: list = None

    def __init__(self, size) -> None:
        self.size = size
        self.data = []


    def push(self, value) -> None:
        assert len(self.data) < self.size, f"stack overflow: {value}"

        self.data.append(value)

    
    def pop(self):
        return self.data.pop() if len(self.data) > 0 else 0


    def peek(self):
        return self.data[-1] if len(self.data) > 0 else 0
    