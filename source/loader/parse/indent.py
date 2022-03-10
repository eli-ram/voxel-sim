class Indent:
    def __init__(self, value: str, step: str, pad: str) -> None:
        self.value = value
        self.step = step
        self.pad = pad
        self.string = "\n" + self.value + self.pad

    def next(self):
        return Indent(self.value + self.step, self.step, self.pad)

    def __str__(self) -> str:
        return self.string

    def __add__(self, other: str) -> str:
        return self.string + other

    def __radd__(self, other: str) -> str:
        return other + self.string