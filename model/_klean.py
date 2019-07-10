# Base Regular Expression Objects
from collections.abc import Sized
from functools import total_ordering

def _str_to_klean_obj(string):
    if isinstance(string, Klean):
        return string
    try:
        # if it can be a Literal it should; otherwise Sequence will Literal-ize it
        return Literal(string)
    except ValueError:
        return Sequence(string)

class Klean(object):
    #Parent Regular Expression Object
    #TODO: Metaclass
    pass

class Operator(Klean):
    # Alter a match pattern
    # Each Operator must be defined as a subclass that pre-defines the following as instance variables
    op = ''
    short_desc = ''

    def __init__(self):
        raise NotImplementedError

    def __str__(self):
        if self.short_desc:
            return f'<{self.short_desc}>'
        return self.metachar

@total_ordering
class Literal(Klean):
    # A literal character to match
    def __init__(self, character):
        #if isinstance(character, Literal):
        #    return self.__init__(Literal.character)
        if not isinstance(character, str) or len(character) != 1:
            raise ValueError(f'{self.__class__.__name__} can only take a single character')
        self.char = character

    def __hash__(self):
        return hash(self.char)

    def __eq__(self, rhs):
        if isinstance(rhs, Literal):
            return self.char == rhs.char
        return NotImplemented

    def __lt__(self, rhs):
        if isinstance(rhs, Literal):
            return self.char < rhs.char
        return NotImplemented

    def __and__(self, rhs):
        if isinstance(rhs, str) and len(rhs) > 0:
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, (Literal, Abstract)):
            return Sequence(self, rhs)
        elif isinstance(rhs, Sequence):
            return Sequence(*([self] + rhs.characters))
        elif isinstance(rhs, (Range, Group)):
            return Group(self, rhs)
        else:
            return NotImplemented

    def __rand__(self, lhs):
        if isinstance(lhs, str) and len(lhs) > 0:
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, (Literal, Abstract)):
            return Sequence(lhs, self)
        elif isinstance(lhs, Sequence):
            return Sequence(*(lhs.characters + [self]))
        elif isinstance(lhs, (Range, Group)):
            return Group(lhs, self)
        else:
            return NotImplemented

    def __or__(self, rhs):
        if isinstance(rhs, str) and len(rhs) > 0:
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, Literal):
            return Range(self, rhs)
        elif isinstance(rhs, Range):
            return Range(*(set((self,)) | rhs.range))
        elif isinstance(rhs, (Abstract, Sequence, Group)):
            return Group(self, rhs, OR=True)
        else:
            return NotImplemented

    def __ror__(self, lhs):
        if isinstance(lhs, str) and len(lhs) > 0:
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, Literal):
            return Range(lhs, self)
        elif isinstance(lhs, Range):
            return Range(*(lhs.range | set((self,))))
        elif isinstance(lhs, (Abstract, Sequence, Group)):
            return Group(lhs, self, OR=True)
        else:
            return NotImplemented

    def __str__(self):
        return self.char

class Abstract(Klean):
    # Match a portion of a string not able to be represented by a character
    # Each Abstract must be defined as a subclass that pre-defines the following as instance variables
    metachar = ''
    short_desc = ''
    # empty string

    def __init__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(self.metachar)

    def __eq__(self, rhs):
        if isinstance(rhs, Abstract):
            return self.metachar == rhs.metachar
        return NotImplemented

    def __and__(self, rhs):
        if isinstance(rhs, str) and len(rhs) > 0:
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, (Literal, Abstract)):
            return Sequence(self, rhs)
        elif isinstance(rhs, Sequence):
            return Sequence(*([self] + rhs.characters))
        elif isinstance(rhs, (Range, Group)):
            return Group(self, rhs)
        else:
            return NotImplemented

    def __rand__(self, lhs):
        if isinstance(lhs, str) and len(lhs) > 0:
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, (Literal, Abstract)):
            return Sequence(lhs, self)
        elif isinstance(lhs, Sequence):
            return Sequence(*(lhs.characters + [self]))
        elif isinstance(lhs, (Range, Group)):
            return Group(lhs, self)
        else:
            return NotImplemented

    def __or__(self, rhs):
        if isinstance(rhs, str) and len(rhs) > 0:
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, Klean):
            return Group(self, rhs, OR=True)
        else:
            return NotImplemented

    def __ror__(self, lhs):
        if isinstance(lhs, str) and len(lhs) > 0:
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, Klean):
            return Group(lhs, self, OR=True)
        else:
            return NotImplemented

    def __str__(self):
        if self.short_desc:
            return f'<{self.short_desc}>'
        return self.metachar

class Sequence(Klean):
    # Multiple Literals anded together
    def __init__(self, *characters):
        # flatten any multi-character strings or Sequences
        characters = list(characters)
        for i in range(len(characters)-1, -1, -1):
            if isinstance(characters[i], Sized) and len(characters[i]) > 1:
                c = characters.pop(i)
                characters[i:i] = [_c for _c in c]
        if not characters or not any(characters):
            raise ValueError('No values provided')
        self.characters = [(c if isinstance(c, (Literal, Abstract)) else Literal(c)) for c in characters]

    def __eq__(self, rhs):
        if isinstance(rhs, Sequence):
            return self.characters ==  rhs.characters
        return NotImplemented

    def __and__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, (Literal, Abstract)):
            return Sequence(*(self.characters + [rhs]))
        elif isinstance(rhs, Sequence):
            return Sequence(*[self.characters + rhs.characters])
        elif isinstance(rhs, Range):
            return Group(self, rhs, OR=True)
        elif isinstance(rhs, Group):
            return Group(self, rhs)
        else:
            return NotImplemented

    def __rand__(self, lhs):
        if isinstance(lhs, str):
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, (Literal, Abstract)):
            return Sequence(*([lhs] + self.characters))
        elif isinstance(lhs, Sequence):
            return Sequence(*[lhs.characters + self.characters])
        elif isinstance(lhs, Range):
            return Group(lhs, self, OR=True)
        elif isinstance(lhs, Group):
            return Group(lhs, self)
        else:
            return NotImplemented

    def __or__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, Klean):
            return Group(self, rhs, OR=True)
        else:
            return NotImplemented

    def __ror__(self, lhs):
        if isinstance(lhs, str):
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, Klean):
            return Group(lhs, self, OR=True)
        else:
            return NotImplemented

    def __str__(self):
        return ''.join(str(char) for char in self.characters)

    def __len__(self):
        return len(self.characters)

class Range(Klean):
    # A compact representation of multiple literals
    def __init__(self, *args, invert=False):

        self.invert = invert
        self.range = set()
        for literal in args:
            try:
                start, end = literal
            except (ValueError, TypeError):
                start = end = literal
            start = getattr(start, 'char', start)
            end = getattr(end, 'char', end)
            if not start or not end:
                raise ValueError('Empty value passed in')
            for char in range(ord(start), ord(end)+1):
                self.range.add(Literal(chr(char)))

    def __eq__(self, rhs):
        if isinstance(rhs, Range):
            return self.range ==  rhs.range and self.invert == rhs.invert
        return NotImplemented

    def __not__(self):
        self.invert = not self.invert

    def __and__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, Klean):
            return Group(self, rhs)
        else:
            return NotImplemented

    def __rand__(self, lhs):
        if isinstance(lhs, str):
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, Klean):
            return Group(lhs, self)
        else:
            return NotImplemented

    def __or__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_klean_obj(rhs)

        if isinstance(rhs, Literal):
            return Range(*(self.range | set((rhs,))))
        elif isinstance(rhs, Range):
            return Range(self.range | rhs.range)
        elif isinstance(rhs, (Abstract, Sequence, Group)):
            return Group(self, rhs, OR=True)
        else:
            return NotImplemented

    def __ror__(self, lhs):
        if isinstance(lhs, str):
            lhs = _str_to_klean_obj(lhs)

        if isinstance(lhs, Literal):
            return Range(*(set((lhs,)) | self.range))
        elif isinstance(lhs, Range):
            return Range(*(lhs.range | self.range))
        elif isinstance(lhs, (Abstract, Sequence, Group)):
            return Group(lhs, self, OR=True)
        else:
            return NotImplemented

    def __str__(self):
        invert = str(Not()) if self.invert else ''
        return f'{{{invert}{",".join(sorted([c.char for c in self.range]))}}}'

class Group(Klean):
    # A group of pattern matches; either literals or other groups or both

    def __init__(self, *groups, repetition=None, OR=False):
        assert all(isinstance(g, Klean) for g in groups)
        self.groups = groups
        self.OR = OR
        if repetition is None:
            repetition = Quantification(min=1, max=1)
        self.repetition = repetition

    def __eq__(self, rhs):
        if isinstance(rhs, Group):
            return self.groups ==  rhs.groups and self.repetition == rhs.repetition
        return NotImplemented

    def __and__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_klean_obj(rhs)
        if isinstance(rhs, Klean):
            return Group(self, rhs)
        else:
            return NotImplemented

    def __or__(self, rhs):
        if isinstance(rhs, str):
            rhs = _str_to_reo_obj(rhs)
        if isinstance(rhs, Klean):
            return Group(self, rhs, OR=True)
        else:
            return NotImplemented

    def __str__(self):
        between = '<OR>' if self.OR else ''
        return f'({between.join([str(g) for g in self.groups])}){self.repetition}'

# Pre-built ranges:
# ALL (*)
# WORD (\w)
# CHARACTERS ([a-zA-Z)
# DECIMAL (\d)
# WHITESPACE (\s)

class Quantification(object):
    # A repitition to apply to a pattern; inclusive
    # A max of 0 means infinity
    # if max < min, max = min
    # * == min=0, max=0
    # + == min=1, max=0
    # ? == min=0, max=1
    def __init__(self, min=0, max=0, greedy=True):
        if type(min) != int or min < 0:
            print("@@@@", min, type(min))
            raise ValueError('min must be an unsigned intiger')
        if type(max) != int or max < 0:
            print("@@@@", max, type(min))
            raise ValueError('max must be an unsigned intiger')
        if max < min and max != 0:
            max = min
        self.min = min
        self.max = max
        self.greedy = bool(greedy)

    def __eq__(self, rhs):
        if isinstance(rhs, Quantification):
            return self.min == rhs.min and self.max == rhs.max and self.greedy == rhs.greedy
        return NotImplemented

    def __str__(self):
        return f'<{self.min},{self.max or ""}{"GREATEST" if self.greedy else "LEAST"}>'
