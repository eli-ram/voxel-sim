from typing import NamedTuple

class Format(NamedTuple):
    initial: str = ''
    prefix: str = ''
    step: str = '  '
    postfix: str = ''
    list_unchanged: bool = True
    list_errors: bool = False

    def indent(self, string: str):
        return '\n' + self.prefix + string + self.postfix

    def next(self, string: str):
        return Fmt(string + self.step, self)
    
    def init(self):
        return self.next('')

class Fmt:
    def __init__(self, string: str, format: Format) -> None:
        self.string = string
        self.format = format
        
    def next(self):
        return self.format.next(self.string)

    def indent(self):
        return self.format.indent(self.string)
