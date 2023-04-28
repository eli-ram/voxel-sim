import traceback

def what(e: Exception) -> str:
    name = e.__class__.__name__
    args = ", ".join(str(arg) for arg in e.args)
    return f"{name}[{args}]"


def trace(e: Exception) -> str:
    _, *trace = traceback.format_tb(e.__traceback__, None)
    where = "\n" + "\n".join(trace)
    return where.replace('\n', '\n\t|')

class ParseError(Exception):
    """ Error for any Parse Fault """
    
class CastError(ParseError):
    """ Error for any Casting Fault """