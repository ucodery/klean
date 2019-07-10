import pytest

from model._klean import Abstract, Group, Literal, Range, Sequence, Quantification
from model.representations import Any, Decimal, LineEnd, LineStart, NotDecimal,\
    NotWhitespace, NotWord, NotWordBoundary, StringEnd, StringStart,\
    Whitespace, Word, WordBoundary
from resolvers.python import format, _format_abstract, _format_group, _format_literal,\
    _format_quantification, _format_range, _format_sequence

@pytest.mark.parametrize("quantity,expected", [
    (Quantification(min=0, max=0, greedy=True), '*'),
    (Quantification(min=0, max=1, greedy=True), '?'),
    (Quantification(min=0, max=2, greedy=True), '{0,2}'),
    (Quantification(min=0, max=10, greedy=True), '{0,10}'),
    (Quantification(min=0, max=9999, greedy=True), '{0,9999}'),
    (Quantification(min=0, max=0, greedy=False), '*?'),
    (Quantification(min=0, max=1, greedy=False), '??'),
    (Quantification(min=0, max=2, greedy=False), '{0,2}?'),
    (Quantification(min=0, max=10, greedy=False), '{0,10}?'),
    (Quantification(min=0, max=9999, greedy=False), '{0,9999}?'),
    (Quantification(min=1, max=0, greedy=True), '+'),
    (Quantification(min=1, max=1, greedy=True), ''),
    (Quantification(min=1, max=2, greedy=True), '{1,2}'),
    (Quantification(min=1, max=10, greedy=True), '{1,10}'),
    (Quantification(min=1, max=9999, greedy=True), '{1,9999}'),
    (Quantification(min=1, max=0, greedy=False), '+?'),
    (Quantification(min=1, max=1, greedy=False), ''),
    (Quantification(min=1, max=2, greedy=False), '{1,2}?'),
    (Quantification(min=1, max=10, greedy=False), '{1,10}?'),
    (Quantification(min=1, max=9999, greedy=False), '{1,9999}?'),
    (Quantification(min=2, max=0, greedy=True), '{2,}'),
    (Quantification(min=2, max=2, greedy=True), '{2}'),
    (Quantification(min=2, max=10, greedy=True), '{2,10}'),
    (Quantification(min=2, max=9999, greedy=True), '{2,9999}'),
    (Quantification(min=2, max=0, greedy=False), '{2,}?'),
    (Quantification(min=2, max=2, greedy=False), '{2}?'),
    (Quantification(min=2, max=10, greedy=False), '{2,10}?'),
    (Quantification(min=2, max=9999, greedy=False), '{2,9999}?'),
    (Quantification(min=10, max=0, greedy=True), '{10,}'),
    (Quantification(min=10, max=10, greedy=True), '{10}'),
    (Quantification(min=10, max=9999, greedy=True), '{10,9999}'),
    (Quantification(min=10, max=0, greedy=False), '{10,}?'),
    (Quantification(min=10, max=10, greedy=False), '{10}?'),
    (Quantification(min=10, max=9999, greedy=False), '{10,9999}?'),
    (Quantification(min=9999, max=0, greedy=True), '{9999,}'),
    (Quantification(min=9999, max=9999, greedy=True), '{9999}'),
    (Quantification(min=9999, max=0, greedy=False), '{9999,}?'),
    (Quantification(min=9999, max=9999, greedy=False), '{9999}?'),
])
def test_format_quantification(quantity, expected):
    assert _format_quantification(quantity) == expected

@pytest.mark.parametrize("literal,expected", [
    (Literal('A'), 'A'),
    (Literal('z'), 'z'),
    (Literal('0'), '0'),
    (Literal('1'), '1'),
    (Literal('\u03A9'), '\u03A9'),
    (Literal('\u03B8'), '\u03B8'),
    (Literal('|'), r'\|'),
    (Literal('^'), r'\^'),
    (Literal('('), r'\('),
    (Literal(']'), r'\]'),
    (Literal('$'), r'\$'),
    (Literal('*'), r'\*'),
    (Literal('~'), r'\~'),
    (Literal('\\'), '\\\\'),
])
def test_format_literal(literal, expected):
    assert _format_literal(literal) == expected

@pytest.mark.parametrize("abstract,expected", [
    (StringStart(), r'\A'),
    (StringEnd(), r'\Z'),
    (LineStart(), '^'),
    (LineEnd(), '$'),
    (WordBoundary(), r'\b'),
    (NotWordBoundary(), r'\B'),
    (Decimal(), r'\d'),
    (NotDecimal(), r'\D'),
    (Whitespace(), r'\s'),
    (NotWhitespace(), r'\S'),
    (Word(), r'\w'),
    (NotWord(), r'\W'),
    (Any(), '.'),
])
def test_format_abstract(abstract, expected):
    assert _format_abstract(abstract) == expected

class DummyPosition(Abstract):
    def __init__(self):
        self.metachar = '\\p'
        self.short_desc = 'TEST'

@pytest.mark.parametrize("illegal", [
    Literal('A'),
    DummyPosition(),
])
def test_format_abstract_runtime_error(illegal):
    with pytest.raises(RuntimeError):
        _format_abstract(illegal)

@pytest.mark.parametrize("illegal", [
    Quantification(),
    Range(('A', 'z')),
    Group(Literal('0'), Literal('1')),
])
def test_format_abstract_type_error(illegal):
    with pytest.raises(TypeError):
        _format_abstract(illegal)

@pytest.mark.parametrize("range,expected", [
    (Range('A', invert=False), '[A]'),
    (Range('A', 'B', 'z', invert=False), '[ABz]'),
    (Range('A', '%', '-', invert=False), r'[%\-A]'),
    (Range('z', 'z', '%', '^', invert=False), r'[%\^z]'),
    (Range('A', '\u03A9', 'z', '\u03B0', invert=False), '[Az\u03A9\u03B0]'),
    (Range('A', invert=True), '[^A]'),
    (Range('A', 'B', 'z', invert=True), '[^ABz]'),
    (Range('A', '%', '-', invert=True), r'[^%\-A]'),
    (Range('z', 'z', '%', '^', invert=True), r'[^%\^z]'),
    (Range('A', '\u03A9', 'z', '\u03B0', invert=True), '[^Az\u03A9\u03B0]'),
])
def test_format_range(range, expected):
    assert _format_range(range) == expected

@pytest.mark.parametrize("illegal", [
    #TODO
])
def test_format_range_runtime_error(illegal):
    with pytest.raises(RuntimeError):
        _format_range(illegal)

@pytest.mark.parametrize("sequence,expected", [
    (Sequence('A'), 'A'),
    (Sequence(('A', 'B', 'z')), 'ABz'),
    (Sequence('A', '%-'), r'A%\-'),
    (Sequence('z', 'z', '%', '^'), r'zz%\^'),
    (Sequence('A\u03A9', 'z\u03B0'), 'A\u03A9z\u03B0'),
])
def test_format_sequence(sequence, expected):
    assert _format_sequence(sequence) == expected

@pytest.mark.parametrize("illegal", [
    #TODO
])
def test_format_sequence_runtime_error(illegal):
    with pytest.raises(RuntimeError):
        _format_sequence(illegal)

@pytest.mark.parametrize("group,expected", [
    (Group(Literal('A'), Literal('B'), OR=False), '(AB)'),
    (Group(Range('A', 'B'), Literal('z'), OR=False), '([AB]z)'),
    (Group(Literal('A'), Sequence('%-'), OR=False), r'(A%\-)'),
    (Group(Group(Literal('z'), Literal('z'), OR=False), Range('%', '^')), r'((zz)[%\^])'),
    (Group(Sequence('A\u03A9', 'z\u03B0'), OR=False), '(A\u03A9z\u03B0)'),
    (Group(Literal('A'), Literal('B'), OR=True), '(A|B)'),
    (Group(Range('A', 'B'), Literal('z'), OR=True), '([AB]|z)'),
    (Group(Literal('A'), Sequence('%-'), OR=True), r'(A|%\-)'),
    (Group(Group(Literal('z'), Literal('z')), Range('%', '^'), OR=True), r'((zz)|[%\^])'),
    (Group(Sequence('A\u03A9', 'z\u03B0'), OR=True), '(A\u03A9z\u03B0)'),
])
def test_format_group(group, expected):
    assert _format_group(group) == expected

@pytest.mark.parametrize("illegal", [
    #TODO
])
def test_format_group_illegal(illegal):
    with pytest.raises(RuntimeError):
        _format_group(illegal)

@pytest.mark.parametrize("input,expected", [
    (Group(Literal('A'), Literal('B'), OR=False), '(AB)'),
    (Group(Range('A', 'B'), Literal('z'), OR=False), '([AB]z)'),
    (Group(Literal('A'), Sequence('%-'), OR=False), r'(A%\-)'),
    (Group(Group(Literal('z'), Literal('z'), OR=False), Range('%', '^')), r'((zz)[%\^])'),
    (Group(Sequence('A\u03A9', 'z\u03B0'), OR=False), '(A\u03A9z\u03B0)'),
    (Group(Literal('A'), Literal('B'), OR=True), '(A|B)'),
    (Group(Range('A', 'B'), Literal('z'), OR=True), '([AB]|z)'),
    (Group(Literal('A'), Sequence('%-'), OR=True), r'(A|%\-)'),
    (Group(Group(Literal('z'), Literal('z')), Range('%', '^'), OR=True), r'((zz)|[%\^])'),
    (Group(Sequence('A\u03A9', 'z\u03B0'), OR=True), '(A\u03A9z\u03B0)'),
])
def test_format(input, expected):
    assert format(input) == expected

@pytest.mark.parametrize("illegal", [
    None,
    "",
    [],
    {},
    42,
])
def test_format_illegal(illegal):
    with pytest.raises(ValueError):
        format(illegal)
