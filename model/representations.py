"""Define all recognized Character Class escapes
Not all of these classes will be recognized by all RegEx systems
"""
import string

from model._klean import Abstract, Literal, Operator, Range, Sequence

# All possible abstract characters

class StringStart(Abstract):
    """Start of String"""

    def __init__(self):
        self.metachar = '\A'
        self.short_desc = 'SOS'

class StringEnd(Abstract):
    """End of String"""

    def __init__(self):
        self.metachar = '\Z'
        self.short_desc = 'EOS'

class LineStart(Abstract):
    """Start of Line"""
    # sometimes equivilant to StringStart

    def __init__(self):
        self.metachar = '^'
        self.short_desc = 'SOL'

class LineEnd(Abstract):
    """End of Line"""
    # sometimes equivilant to StringEnd

    def __init__(self):
        self.metachar = '$'
        self.short_desc = 'EOL'

class WordBoundary(Abstract):
    """Start or end of a word"""

    def __init__(self):
        self.metachar = '\b'
        self.short_desc = 'WB'

class NotWordBoundary(Abstract):
    """Anywhere but the start or end of a word"""

    def __init__(self):
        self.metachar = '\B'
        self.short_desc = 'NWB'

class Decimal(Abstract):
    """Base 10 digits"""

    def __init__(self):
        self.metachar = '\d'
        self.short_desc = 'D'

class NotDecimal(Abstract):
    """Anything but a base 10 digit"""

    def __init__(self):
        self.metachar = '\D'
        self.short_desc = 'ND'

class Whitespace(Abstract):
    """Any Whitespace character"""

    def __init__(self):
        self.metachar = '\s'
        self.short_desc = 'SPACE'

class NotWhitespace(Abstract):
    """Any character but whitespace"""

    def __init__(self):
        self.metachar = '\S'
        self.short_desc = 'NSPACE'

class Word(Abstract):
    """Any character that can make up a word"""

    def __init__(self):
        self.metachar = '\w'
        self.short_desc = 'WORD'

class NotWord(Abstract):
    """Any character that cannot make up a word"""

    def __init__(self):
        self.metachar = '\W'
        self.short_desc = 'NWORD'

class Any(Abstract):
    """Any Single Character except a newline"""

    def __init__(self):
        self.metachar = '.'
        self.short_desc = 'ANY'

class AnyAtAll(Abstract):
    """Any Single Character including a newline"""

    def __init__(self):
        self.metachar = '.'
        self.short_desc = 'ANY'

# All possible operators

class Or(Operator):
    def __init__(self):
        self.op = '|'
        self.short_desc = 'OR'

class Not(Operator):
    def __init__(self):
        self.op = '^'
        self.short_desc = 'NOT'

# some pre-built character sequences

class Empty(Sequence):
    """Match a line with no characters in it"""

    def __init__(self):
        self.characters = [StringStart, StringEnd]

# Some pre-built character ranges

class LowerAscii(Range):
    """Match any lower case ascii character"""

    def __init__(self):
        super(LowerAscii, self).__init__(string.ascii_lowercase[0], string.ascii_lowercase[-1])

class UpperAscii(Range):
    """Match any upper case ascii character"""

    def __init__(self):
        super(UpperAscii, self).__init__(string.ascii_uppercase[0], string.ascii_uppercase[-1])

class Hex(Range):
    """Match any hexidecimal character"""

    def __init__(self):
        digits = string.digit + 'aAbBcCdDeEfF'
        super(Hex, self).__init__(string.digits)
