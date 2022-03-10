
class ParseError(Exception):
    """ Error for any Parse Fault """

    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self) -> str:
        if not self.message:
            return ''
        name = type(self).__name__
        return f"### {name}({self.message})"

class CastError(ParseError):
    """ Error for any Casting Fault """