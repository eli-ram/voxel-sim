
class ParseError(Exception):
    """ Error for any Parse Fault """
    
class CastError(ParseError):
    """ Error for any Casting Fault """