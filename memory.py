class Memory:
    mem: list = None
    size = None

    def __init__(self, data: list, size) -> None:
        self.size = size

        self.mem = [0] * size

        for i in range(len(data)):
            self.mem[i] = data[i]

    def read(self, addr: int):
        assert 0 <= addr < self.size, f"out of memory: {addr}"

        return self.mem[addr]

    def write(self, addr: int, value) -> None:
        assert 0 <= addr < self.size, f"out of memory: {addr}"

        self.mem[addr] = value


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
