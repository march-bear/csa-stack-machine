class Memory:
    mem: list = None
    size = None

    def __init__(self, data: list, size) -> None:
        self.size = size

        self.mem = [0] * size
        
        for i in range(len(data)):
            self.mem[i] = data[i]


    def read(self, addr):
        assert 0 <= addr < self.size, f"out of memory: {addr}"

        return self.mem[addr]
    

    def write(self, addr, value) -> None:
        assert 0 <= addr < self.size, f"out of memory: {addr}"

        self.mem[addr] = value
