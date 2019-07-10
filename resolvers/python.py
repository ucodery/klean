"""Return a Klean object as valid python re string"""

import re

from model._klean import Abstract, Group, Klean, Literal, Range, Sequence, Quantification
from model.representations import StringStart, StringEnd, LineStart, LineEnd, WordBoundary,\
    NotWordBoundary, Decimal, NotDecimal, Whitespace, NotWhitespace, Word,\
    NotWord, Any

def _format_quantification(quantity):
    repeat = ''
    if quantity.max == 0:
        if quantity.min == 0:
            repeat = '*'
        elif quantity.min == 1:
            repeat = '+'
        else:
            repeat = f'{{{quantity.min},}}'
    elif quantity.max == 1 and quantity.min == 0:
        repeat = '?'
    elif quantity.max == quantity.min:
        if quantity.max == 1:
            return ''
        repeat = f'{{{quantity.max}}}'
    else:
        repeat = f'{{{quantity.min},{quantity.max}}}'

    if not quantity.greedy:
        repeat += '?'
    return repeat

def _format_literal(klean):
    return str(re.escape(klean.char))

ABSTRACTS = {
    StringStart(): r'\A',
    StringEnd(): r'\Z',
    LineStart(): r'^',
    LineEnd(): r'$',
    WordBoundary(): r'\b',
    NotWordBoundary(): r'\B',
    Decimal(): r'\d',
    NotDecimal(): r'\D',
    Whitespace(): r'\s',
    NotWhitespace(): r'\S',
    Word(): r'\w',
    NotWord(): r'\W',
    Any(): r'.',
    }
def _format_abstract(klean):
    if klean in ABSTRACTS:
        if isinstance(ABSTRACTS[klean], Klean):
            raise RuntimeWarning(f'{type(klean)} is not natively supported'
                                 'in python Regular Expressions, substituting'
                                 f'{ABSTRACTS[klean]}')
        return ABSTRACTS[klean]
    raise RuntimeError(f'{type(klean)} is not supported in python Regular'
                       'Expressions')

RANGE_START = '['
RANGE_END = ']'
RANGE_CONT = '-'
RANGE_NOT = '^'
def _format_range(klean):
    # A range can only contain literals, but location is important for negation
    range = f'{RANGE_START}{RANGE_NOT if klean.invert else ""}'
    #TODO collapse consecutive characters into A-Z
    #NOTE for now, sort to prep for combining adjacent chars
    for next in sorted(klean.range):
        if not isinstance(next, Literal):
            raise RuntimeError(f'{type(klean)} is not supported in python '
                               'Regular Expression Ranges')
        range += _format_literal(next)
    return f'{range}{RANGE_END}'

def _format_sequence(klean):
    sequence = ''
    for next in klean.characters:
        if isinstance(next, Literal):
            sequence += _format_literal(next)
        elif isinstance(next, Abstract):
            sequence += _format_abstract(next)
        else:
            raise RuntimeError(f'{type(next)} is not supported in python '
                               'Regular Expression Sequences')
    return sequence

GROUP_START = '('
GROUP_END = ')'
GROUP_OR = '|'
def _format_group(klean):
    #TODO: groups should not add "()"s if they are not needed. i.e. double paren
    # or no inner contents need to be contained
    #TODO: if OR and if a group is a sequence, it needs its own parentheses
    #TODO: if two sides of an OR are rangees and/or literals, compine into one range
    group = (GROUP_OR if klean.OR else "").join([format(sub) for sub in klean.groups])
    quantity = _format_quantification(klean.repetition)
    return f'{GROUP_START}{group}{GROUP_END}{quantity}'

#TODO: rename, format is a built-in
def format(klean):
    if isinstance(klean, Group):
        return _format_group(klean)
    if isinstance(klean, Sequence):
        return _format_sequence(klean)
    if isinstance(klean, Range):
        return _format_range(klean)
    if isinstance(klean, Literal):
        return _format_literal(klean)
    if isinstance(klean, Abstract):
        return _format_abstract(klean)
    else:
        raise ValueError(f'format must be supplied with a Klean object, recieved {type(klean)} instead')
