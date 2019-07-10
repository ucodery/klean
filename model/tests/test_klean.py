import pytest

from model._klean import Abstract, Group, Literal, Range, Sequence, Quantification

def test_quantification():
    quantity = Quantification()
    assert quantity == Quantification(0, 0, True)
    quantity = Quantification(min=1, greedy=True)
    assert quantity == Quantification(1, 0, True)
    quantity = Quantification(max=2, greedy=False)
    assert quantity == Quantification(0, 2, False)
    quantity = Quantification(greedy=False)
    assert quantity == Quantification(0, 0, False)
    quantity = Quantification(min=2, max=1)
    assert quantity == Quantification(2, 1, True)
    quantity = Quantification(min=2, max=0)
    assert quantity == Quantification(2, 0, True)
    quantity = Quantification(min=2, max=4)
    assert quantity == Quantification(2, 4, True)
    quantity = Quantification(min=0, max=4)
    assert quantity == Quantification(0, 4, True)
    quantity = Quantification(min=0, max=1, greedy=False)
    assert quantity == Quantification(0, 1, False)

def test_quantification_illegal():
    with pytest.raises(ValueError):
        Quantification(1.2, 3)
    with pytest.raises(ValueError):
        Quantification(1, 3.5)
    with pytest.raises(ValueError):
        Quantification(-1, 2)
    with pytest.raises(ValueError):
        Quantification(1, -2)
    with pytest.raises(ValueError):
        Quantification(None)
    with pytest.raises(ValueError):
        Quantification(True)
    with pytest.raises(ValueError):
        Quantification('1')
    with pytest.raises(ValueError):
        Quantification([])
    with pytest.raises(ValueError):
        Quantification({})
    with pytest.raises(ValueError):
        Quantification(())

def test_literal():
    literal = Literal('a')
    assert str(literal) == 'a'
    literal = Literal('Z')
    assert str(literal) == 'Z'
    literal = Literal('!')
    assert str(literal) == '!'
    literal = Literal(' ')
    assert str(literal) == ' '
    literal = Literal('a')
    assert str(literal) == 'a'
    literal = Literal('\u03A9')
    assert str(literal) == '\u03A9'

def test_literal_illegal():
    with pytest.raises(ValueError):
        Literal(None)
    with pytest.raises(ValueError):
        Literal('foo')
    with pytest.raises(ValueError):
        Literal('')
    with pytest.raises(ValueError):
        Literal(42)
    with pytest.raises(ValueError):
        Literal(None)
    literal = Literal('A')
    with pytest.raises(ValueError):
        Literal(literal)

def test_literal_and():
    forward = Literal('R') & 'E'
    backward = 'R' & Literal('E')
    assert forward == backward
    assert forward == Sequence('R', 'E')

    forward = Literal('R') & 'ED'
    backward = 'RE' & Literal('D')
    assert forward == backward
    assert forward == Sequence('R', 'E', 'D')

    forward = Literal('R') & Literal('E')
    assert forward == Sequence('R', 'E')

    forward = Literal('R') & Sequence('E')
    backward = Sequence('R') & Literal('E')
    assert forward == backward
    assert forward == Sequence('R', 'E')

    forward = Literal('R') & Sequence('E', 'D')
    backward = Sequence('R', 'E') & Literal('D')
    assert forward == backward
    assert forward == Sequence('R', 'E', 'D')

    forward = Literal('R') & Range('E')
    backward = Range('R') & Literal('E')
    assert forward != backward
    assert forward == Group(Literal('R'), Range('E'))
    assert backward == Group(Range('R'), Literal('E'))

    forward = Literal('R') & Range(('E', 'D'))
    backward = Range(('R', 'E')) & Literal('D')
    assert forward != backward
    assert forward == Group(Literal('R'), Range(('E', 'D')))
    assert backward == Group(Range(('R', 'E')), Literal('D'))

    forward = Literal('R') & Group(*(Literal('E'),))
    backward = Group(*(Literal('R'),)) & Literal('E')
    assert forward != backward
    assert forward == Group(Literal('R'), Group(*(Literal('E'),)))
    assert backward == Group(Group(*(Literal('R'),)), Literal('E'))

    forward = Literal('R') & Group(*(Literal('E'), Literal('D')))
    backward = Group(*(Literal('R'), Literal('E'))) & Literal('D')
    assert forward != backward
    assert forward == Group(Literal('R'), Group(*(Literal('E'), Literal('D'))))
    assert backward == Group(Group(*(Literal('R'), Literal('E'))), Literal('D'))

def test_literal_and_illegal():
    with pytest.raises(TypeError):
        forward = Literal('R') & None
    with pytest.raises(TypeError):
        backward = None & Literal('R')
    with pytest.raises(TypeError):
        forward = Literal('R') & ''
    with pytest.raises(TypeError):
        backward = '' & Literal('R')
    with pytest.raises(TypeError):
        forward = Literal('R') & 42
    with pytest.raises(TypeError):
        backward = 42 & Literal('R')

def test_literal_or():
    forward = Literal('R') | 'E'
    backward = 'R' | Literal('E')
    assert forward == backward
    assert forward == Range('R', 'E')

    forward = Literal('R') | 'ED'
    backward = 'RE' | Literal('D')
    assert forward != backward
    assert forward == Group(Literal('R'), Sequence('E', 'D'), OR=True)
    assert backward == Group(Sequence('R', 'E'), Literal('D'), OR=True)

    forward = Literal('R') | Literal('E')
    assert forward == Range('R', 'E')

    forward = Literal('R') | Sequence('E')
    backward = Sequence('R') | Literal('E')
    assert forward != backward
    assert forward == Group(Literal('R'), Sequence('E'), OR=True)
    assert backward == Group(Sequence('R'), Literal('E'), OR=True)

    forward = Literal('R') | Sequence('E', 'D')
    backward = Sequence('R', 'E') | Literal('D')
    assert forward != backward
    assert forward == Group(Literal('R'), Sequence('E', 'D'), OR=True)
    assert backward == Group(Sequence('R', 'E'), Literal('D'), OR=True)

    forward = Literal('R') | Range('E')
    backward = Range('R') | Literal('E')
    assert forward == backward
    assert forward == Range('R', 'E')
    assert backward == Range('R', 'E')

    forward = Literal('R') | Range('E', 'D')
    backward = Range('R', 'E') | Literal('D')
    assert forward == backward
    assert forward == Range('R', 'E', 'D')
    assert backward == Range('R', 'E', 'D')

    forward = Literal('R') | Group(*(Literal('E'),))
    backward = Group(*(Literal('R'),)) | Literal('E')
    assert forward != backward
    assert forward == Group(Literal('R'), Group(*(Literal('E'),)), OR=True)
    assert backward == Group(Group(*(Literal('R'),)), Literal('E'), OR=True)

    forward = Literal('R') | Group(*(Literal('E'), Literal('D')))
    backward = Group(*(Literal('R'), Literal('E'))) | Literal('D')
    assert forward != backward
    assert forward == Group(Literal('R'), Group(*(Literal('E'), Literal('D'))), OR=True)


    assert backward == Group(Group(*(Literal('R'), Literal('E'))), Literal('D'), OR=True)

def test_literal_or_illegal():
    with pytest.raises(TypeError):
        forward = Literal('R') | None
    with pytest.raises(TypeError):
        backward = None | Literal('R')
    with pytest.raises(TypeError):
        forward = Literal('R') | ''
    with pytest.raises(TypeError):
        backward = '' | Literal('R')
    with pytest.raises(TypeError):
        forward = Literal('R') | 42
    with pytest.raises(TypeError):
        backward = 42 | Literal('R')

#TODO abstract child as test fixture
class DummyPosition(Abstract):
    def __init__(self):
        self.metachar = '\\p'
        self.short_desc = 'TEST'

def test_abstract_illegal():
    with pytest.raises(NotImplementedError):
        Abstract()

def test_abstract_and():
    forward = DummyPosition() & 'E'
    backward = 'E' & DummyPosition()
    assert forward != backward
    assert forward == Sequence(DummyPosition(), 'E')
    assert backward == Sequence('E', DummyPosition())

    forward = DummyPosition() & 'ED'
    backward = 'ED' & DummyPosition()
    assert forward != backward
    assert forward == Sequence(DummyPosition(), 'E', 'D')
    assert backward == Sequence('E', 'D', DummyPosition())

    forward = DummyPosition() & DummyPosition()
    assert forward == Sequence(DummyPosition(), DummyPosition())

    forward = DummyPosition() & Literal('E')
    backward = Literal('E') & DummyPosition()
    assert forward != backward
    assert forward == Sequence(DummyPosition(), Literal('E'))
    assert backward == Sequence(Literal('E'), DummyPosition())

    forward = DummyPosition() & Sequence('E')
    backward = Sequence('E') & DummyPosition()
    assert forward != backward
    assert forward == Sequence(DummyPosition(), 'E')
    assert backward == Sequence('E', DummyPosition())

    forward = DummyPosition() & Sequence('E', 'D')
    backward = Sequence('E', 'D') & DummyPosition()
    assert forward != backward
    assert forward == Sequence(DummyPosition(), 'E', 'D')
    assert backward == Sequence('E', 'D', DummyPosition())

    forward = DummyPosition() & Range('E')
    backward = Range('E') & DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Range('E'))
    assert backward == Group(Range('E'), DummyPosition())

    forward = DummyPosition() & Range(('E', 'D'))
    backward = Range(('E', 'D')) & DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Range(('E', 'D')))
    assert backward == Group(Range(('E', 'D')), DummyPosition())

    forward = DummyPosition() & Group(*(DummyPosition(),))
    backward = Group(*(DummyPosition(),)) & DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Group(*(DummyPosition(),)))
    assert backward == Group(Group(*(DummyPosition(),)), DummyPosition())

    forward = DummyPosition() & Group(*(DummyPosition(), DummyPosition()))
    backward = Group(*(DummyPosition(), DummyPosition())) & DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Group(*(DummyPosition(), DummyPosition())))
    assert backward == Group(Group(*(DummyPosition(), DummyPosition())), DummyPosition())

def test_abstract_and_illegal():
    with pytest.raises(TypeError):
        forward = DummyPosition('R') & None
    with pytest.raises(TypeError):
        backward = None & DummyPosition('R')
    with pytest.raises(TypeError):
        forward = DummyPosition('R') & ''
    with pytest.raises(TypeError):
        backward = '' & DummyPosition('R')
    with pytest.raises(TypeError):
        forward = DummyPosition('R') & 42
    with pytest.raises(TypeError):
        backward = 42 & DummyPosition('R')

def test_abstract_or():
    forward = DummyPosition() | 'E'
    backward = 'E' | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Literal('E'), OR=True)
    assert backward == Group(Literal('E'), DummyPosition(), OR=True)

    forward = DummyPosition() | 'ED'
    backward = 'ED' | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Sequence('E', 'D'), OR=True)
    assert backward == Group(Sequence('E', 'D'), DummyPosition(), OR=True)

    forward = DummyPosition() | DummyPosition()
    assert forward == Group(DummyPosition(), DummyPosition(), OR=True)

    forward = DummyPosition() | Literal('E')
    backward = Literal('E') | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Literal('E'), OR=True)
    assert backward == Group(Literal('E'), DummyPosition(), OR=True)

    forward = DummyPosition() | Sequence('E')
    backward = Sequence('E') | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Sequence('E'), OR=True)
    assert backward == Group(Sequence('E'), DummyPosition(), OR=True)

    forward = DummyPosition() | Sequence('E', 'D')
    backward = Sequence('E', 'D') | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Sequence('E', 'D'), OR=True)
    assert backward == Group(Sequence('E', 'D'), DummyPosition(), OR=True)

    forward = DummyPosition() | Range('E')
    backward = Range('E') | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Range('E'), OR=True)
    assert backward == Group(Range('E'), DummyPosition(), OR=True)

    forward = DummyPosition() | Range('E', 'D')
    backward = Range('E', 'D') | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Range('E', 'D'), OR=True)
    assert backward == Group(Range('E', 'D'), DummyPosition(), OR=True)

    forward = DummyPosition() | Group(*(DummyPosition(),))
    backward = Group(*(DummyPosition(),)) | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Group(*(DummyPosition(),)), OR=True)
    assert backward == Group(Group(*(DummyPosition(),)), DummyPosition(), OR=True)

    forward = DummyPosition() | Group(*(DummyPosition(), DummyPosition()))
    backward = Group(*(DummyPosition(), DummyPosition())) | DummyPosition()
    assert forward != backward
    assert forward == Group(DummyPosition(), Group(*(DummyPosition(), DummyPosition())), OR=True)
    assert backward == Group(Group(*(DummyPosition(), DummyPosition())), DummyPosition(), OR=True)

def test_abstract_or_illegal():
    with pytest.raises(TypeError):
        forward = DummyPosition() | None
    with pytest.raises(TypeError):
        backward = None | DummyPosition()
    with pytest.raises(TypeError):
        forward = DummyPosition() | ''
    with pytest.raises(TypeError):
        backward = '' | DummyPosition()
    with pytest.raises(TypeError):
        forward = DummyPosition() | 42
    with pytest.raises(TypeError):
        backward = 42 | DummyPosition()

def test_sequence():
    sequence = Sequence('a')
    assert str(sequence) == 'a'
    sequence = Sequence('a', 'b', 'c')
    sequence_grouped = Sequence('a', 'bc')
    assert sequence == sequence_grouped
    assert str(sequence) == 'abc'
    sequence = Sequence('a_)')
    sequence_grouped = Sequence('a_', ')')
    assert sequence == sequence_grouped
    assert str(sequence) == 'a_)'
    sequence = Sequence('Z', '& ', '"')
    sequence_grouped = Sequence('Z', '&', ' ', '"')
    assert sequence == sequence_grouped
    assert str(sequence) == 'Z& "'
    sequence = Sequence('\u03A9\u03B8\u00B7')
    sequence_grouped = Sequence('\u03A9', '\u03B8', '\u00B7')
    assert sequence == sequence_grouped
    assert str(sequence) == '\u03A9\u03B8\u00B7'

def test_sequence_illegal():
    with pytest.raises(ValueError):
        Sequence('')
    with pytest.raises(ValueError):
        Sequence(('A',))
    with pytest.raises(ValueError):
        Sequence('A', 42)
    with pytest.raises(ValueError):
        Sequence(42)
    with pytest.raises(ValueError):
        Sequence(None)
    with pytest.raises(ValueError):
        Sequence([])
    with pytest.raises(ValueError):
        Sequence([], [])

def test_sequence_and():
    forward = Sequence('A') & 'B'
    backward = 'A' & Sequence('B')
    assert forward == backward
    assert forward == Sequence('AB')

    forward = Sequence('A') & 'BC'
    backward = 'A' & Sequence('BC')
    assert forward == backward
    assert forward == Sequence('ABC')

    forward = Sequence('AB') & 'C'
    backward = 'AB' & Sequence('C')
    assert forward == backward
    assert forward == Sequence('ABC')

    forward = Sequence('AB') & 'CD'
    backward = 'AB' & Sequence('CD')
    assert forward == backward
    assert forward == Sequence('A', 'B', 'C', 'D')

    forward = Sequence('A') & Sequence('B')
    assert forward == Sequence('A', 'B')

    forward = Sequence('AB') & Sequence('CD')
    assert forward == Sequence('AB', 'CD')

    forward = Sequence('A') & Sequence('BC')
    backward = Sequence('AB') & Sequence('C')
    assert forward == backward
    assert forward == Sequence('ABC')

    forward = Sequence('A', 'B', 'C') & Sequence('D', 'E')
    backward = Sequence('A', 'B') & Sequence('C', 'D', 'E')
    assert forward == backward
    assert forward == Sequence('A', 'B', 'C', 'D', 'E')

    forward = Sequence('A') & Range('B')
    backward = Range('A') & Sequence('B')
    assert forward != backward
    assert forward == Group(Sequence('A'), Range('B'))
    assert backward == Group(Range('A'), Sequence('B'))

    forward = Sequence('A') & Range('B', 'C', 'D')
    backward = Range('A') & Sequence('B', 'C', 'D')
    assert forward != backward
    assert forward == Group(Sequence('A'), Range('B', 'C', 'D'))
    assert backward == Group(Range('A'), Sequence('B', 'C', 'D'))

    forward = Sequence('A', 'B', 'C') & Range('D')
    backward = Range('A', 'B', 'C') & Sequence('D')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Range('D'))
    assert backward == Group(Range('A', 'B', 'C'), Sequence('D'))

    forward = Sequence('A', 'B', 'C') & Range('D', 'E', 'F')
    backward = Range('A', 'B', 'C') & Sequence('D', 'E', 'F')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Range('D', 'E', 'F'))
    assert backward == Group(Range('A', 'B', 'C'), Sequence('D', 'E', 'F'))

    forward = Sequence('A') & Group(Literal('B'))
    backward = Group(Literal('A')) & Sequence('B')
    assert forward != backward
    assert forward == Group(Sequence('A'), Group(Literal('B')))
    assert backward == Group(Group(Literal('A')), Sequence('B'))

    forward = Sequence('A') & Group(Sequence('B', 'C', 'D'))
    backward = Group(Literal('A')) & Sequence('B', 'C', 'D')
    assert forward != backward
    assert forward == Group(Sequence('A'), Group(Sequence('B', 'C', 'D')))
    assert backward == Group(Group(Literal('A')), Sequence('B', 'C', 'D'))

    forward = Sequence('A', 'B', 'C') & Group(Literal('D'))
    backward = Group(Sequence('A', 'B', 'C')) & Sequence('D')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Group(Literal('D')))
    assert backward == Group(Group(Sequence('A', 'B', 'C')), Sequence('D'))

    forward = Sequence('A', 'B', 'C') & Group(Sequence('D', 'E', 'F'))
    backward = Group(Sequence('A', 'B', 'C')) & Sequence('D', 'E', 'F')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Group(Sequence('D', 'E', 'F')))
    assert backward == Group(Group(Sequence('A', 'B', 'C')), Sequence('D', 'E', 'F'))

def test_sequence_and_illegal():
    with pytest.raises(TypeError):
        forward = Sequence('A') & None
    with pytest.raises(TypeError):
        backward = None & Sequence('AB')
    with pytest.raises(ValueError):
        forward = Sequence('ABC') & ''
    with pytest.raises(ValueError):
        backward = '' & Sequence('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = Sequence('AAA') & 42
    with pytest.raises(TypeError):
        backward = 42 & Sequence('AA', 'A')
    with pytest.raises(TypeError):
        forward = Sequence('ABC') & ('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = ('A', 'B', 'C') & Sequence('A','B','C')

def test_sequence_or():
    forward = Sequence('A') | 'B'
    backward = 'A' | Sequence('B')
    assert forward != backward
    assert forward == Group(Sequence('A'), Literal('B'), OR=True)
    assert backward == Group(Literal('A'), Sequence('B'), OR=True)

    forward = Sequence('A') | 'BC'
    backward = 'A' | Sequence('BC')
    assert forward != backward
    assert forward == Group(Sequence('A'), Sequence('BC'), OR=True)
    assert backward == Group(Literal('A'), Sequence('BC'), OR=True)

    forward = Sequence('AB') | 'C'
    backward = 'AB' | Sequence('C')
    assert forward != backward
    assert forward == Group(Sequence('AB'), Literal('C'), OR=True)
    assert backward == Group(Sequence('AB'), Sequence('C'), OR=True)

    forward = Sequence('AB') | 'CD'
    backward = 'AB' | Sequence('CD')
    assert forward == backward
    assert forward == Group(Sequence('A', 'B'), Sequence('C', 'D'), OR=True)

    forward = Sequence('A') | Sequence('B')
    assert forward == Group(Sequence('A'), Sequence('B'), OR=True)

    forward = Sequence('AB') | Sequence('CD')
    assert forward == Group(Sequence('AB'), Sequence('CD'), OR=True)

    forward = Sequence('A') | Sequence('BC')
    backward = Sequence('AB') | Sequence('C')
    assert forward != backward
    assert forward == Group(Sequence('A'), Sequence('BC'), OR=True)
    assert backward == Group(Sequence('AB'), Sequence('C'), OR=True)

    forward = Sequence('A', 'B', 'C') | Sequence('D', 'E')
    backward = Sequence('A', 'B') | Sequence('C', 'D', 'E')
    assert forward != backward
    assert forward == Group(Sequence('ABC'), Sequence('DE'), OR=True)
    assert backward == Group(Sequence('AB'), Sequence('CDE'), OR=True)

    forward = Sequence('A') | Range('B')
    backward = Range('A') | Sequence('B')
    assert forward != backward
    assert forward == Group(Sequence('A'), Range('B'), OR=True)
    assert backward == Group(Range('A'), Sequence('B'), OR=True)

    forward = Sequence('A') | Range('B', 'C', 'D')
    backward = Range('A') | Sequence('B', 'C', 'D')
    assert forward != backward
    assert forward == Group(Sequence('A'), Range('B', 'C', 'D'), OR=True)
    assert backward == Group(Range('A'), Sequence('B', 'C', 'D'), OR=True)

    forward = Sequence('A', 'B', 'C') | Range('D')
    backward = Range('A', 'B', 'C') | Sequence('D')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Range('D'), OR=True)
    assert backward == Group(Range('A', 'B', 'C'), Sequence('D'), OR=True)

    forward = Sequence('A', 'B', 'C') | Range('D', 'E', 'F')
    backward = Range('A', 'B', 'C') | Sequence('D', 'E', 'F')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Range('D', 'E', 'F'), OR=True)
    assert backward == Group(Range('A', 'B', 'C'), Sequence('D', 'E', 'F'), OR=True)

    forward = Sequence('A') | Group(Literal('B'))
    backward = Group(Literal('A')) | Sequence('B')
    assert forward != backward
    assert forward == Group(Sequence('A'), Group(Literal('B')), OR=True)
    assert backward == Group(Group(Literal('A')), Sequence('B'), OR=True)

    forward = Sequence('A') | Group(Sequence('B', 'C', 'D'))
    backward = Group(Literal('A')) | Sequence('B', 'C', 'D')
    assert forward != backward
    assert forward == Group(Sequence('A'), Group(Sequence('B', 'C', 'D')), OR=True)
    assert backward == Group(Group(Literal('A')), Sequence('B', 'C', 'D'), OR=True)

    forward = Sequence('A', 'B', 'C') | Group(Literal('D'))
    backward = Group(Sequence('A', 'B', 'C')) | Sequence('D')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Group(Literal('D')), OR=True)
    assert backward == Group(Group(Sequence('A', 'B', 'C')), Sequence('D'), OR=True)

    forward = Sequence('A', 'B', 'C') | Group(Sequence('D', 'E', 'F'))
    backward = Group(Sequence('A', 'B', 'C')) | Sequence('D', 'E', 'F')
    assert forward != backward
    assert forward == Group(Sequence('A', 'B', 'C'), Group(Sequence('D', 'E', 'F')), OR=True)
    assert backward == Group(Group(Sequence('A', 'B', 'C')), Sequence('D', 'E', 'F'), OR=True)

def test_sequence_or_illegal():
    with pytest.raises(TypeError):
        forward = Sequence('A') | None
    with pytest.raises(TypeError):
        backward = None | Sequence('AB')
    with pytest.raises(ValueError):
        forward = Sequence('ABC') | ''
    with pytest.raises(ValueError):
        backward = '' | Sequence('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = Sequence('AAA') | 42
    with pytest.raises(TypeError):
        backward = 42 | Sequence('AA', 'A')
    with pytest.raises(TypeError):
        forward = Sequence('ABC') | ('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = ('A', 'B', 'C') | Sequence('A','B','C')

def test_range():
    range = Range('a')
    assert str(range) == '{a}'
    range = Range('a', 'b', 'c')
    range_grouped = Range(('a', 'c'))
    assert range == range_grouped
    assert str(range) == '{a,b,c}'
    range = Range('a', ('%', ')'))
    range_grouped = Range(('%', ')'))
    assert range != range_grouped
    assert str(range) == '{%,&,\',(,),a}'
    assert str(range_grouped) == '{%,&,\',(,)}'
    range = Range('Z', 'Z', '|', '3', '|')
    range_grouped = Range('Z', '|', '3')
    assert range == range_grouped
    assert str(range) == '{3,Z,|}'
    range = Range('\u03A9', '\u03B0')
    range_grouped = Range(('\u03A9', '\u03B0'))
    assert range != range_grouped
    assert str(range) == '{\u03A9,\u03B0}'
    assert str(range_grouped) == '{\u03A9,\u03AA,\u03AB,\u03AC,\u03AD,\u03AE,\u03AF,\u03B0}'

def test_range_illegal():
    with pytest.raises(ValueError):
        Range('')
    with pytest.raises(TypeError):
        Range(42)
    with pytest.raises(ValueError):
        Range(None)
    with pytest.raises(ValueError):
        Range([])
    with pytest.raises(TypeError):
        Range(('',))
    with pytest.raises(TypeError):
        Range(('Z',))
    with pytest.raises(TypeError):
        Range((42, 24))
    with pytest.raises(ValueError):
        Range('', ('A','B'))

def test_range_and():
    forward = Range('A') & 'B'
    backward = 'A' & Range('B')
    assert forward != backward
    assert forward == Group(Range('A'), Literal('B'))
    assert backward == Group(Literal('A'), Range('B'))

    forward = Range('A') & 'BC'
    backward = 'A' & Range('B', 'C')
    assert forward != backward
    assert forward == Group(Range('A'), Sequence('BC'))
    assert backward == Group(Literal('A'), Range('B', 'C'))

    forward = Range('A', 'B') & 'C'
    backward = 'AB' & Range('C')
    assert forward != backward
    assert forward == Group(Range('A', 'B'), Literal('C'))
    assert backward == Group(Sequence('AB'), Range('C'))

    forward = Range('A', 'B') & 'CD'
    backward = 'AB' & Range('C', 'D')
    assert forward != backward
    assert forward == Group(Range('A', 'B'), Sequence('CD'))
    assert backward == Group(Sequence('AB'), Range('C', 'D'))

    forward = Range('A') & 'BCDE'
    backward = 'A' & Range(('B', 'E'))
    assert forward != backward
    assert forward == Group(Range('A'), Sequence('BCDE'))
    assert backward == Group(Literal('A'), Range(('B', 'E')))

    forward = Range(('A', 'D')) & 'E'
    backward = 'ABCD' & Range('E')
    assert forward != backward
    assert forward == Group(Range(('A', 'D')), Literal('E'))
    assert backward == Group(Sequence('ABCD'), Range('E'))

    forward = Range(('A', 'C')) & 'DE'
    backward = 'AB' & Range(('C', 'E'))
    assert forward != backward
    assert forward == Group(Range(('A', 'C')), Sequence('DE'))
    assert backward == Group(Sequence('AB'), Range(('C', 'E')))

def test_range_and_illegal():
    with pytest.raises(TypeError):
        forward = Range('A') & None
    with pytest.raises(TypeError):
        backward = None & Range('A', 'B')
    with pytest.raises(ValueError):
        forward = Range(('A', 'C')) & ''
    with pytest.raises(ValueError):
        backward = '' & Range('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = Range('A', 'A', 'A') & 42
    with pytest.raises(TypeError):
        backward = 42 & Range('A', 'A', 'A')
    with pytest.raises(TypeError):
        forward = Range('ABC') & ('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = ('A', 'B', 'C') & Range('A','B','C')

def test_range_or():
    forward = Range('A') | 'B'
    backward = 'A' | Range('B')
    assert forward == backward
    assert forward == Range('A', 'B')

    forward = Range('A') | 'BC'
    backward = 'A' | Range('B', 'C')
    assert forward != backward
    assert forward == Group(Range('A'), Sequence('BC'), OR=True)
    assert backward == Range('A', 'B', 'C')

    forward = Range('A', 'B') | 'C'
    backward = 'AB' | Range('C')
    assert forward != backward
    assert forward == Range('A', 'B', 'C')
    assert backward == Group(Sequence('AB'), Range('C'), OR=True)

    forward = Range('A', 'B') | 'CD'
    backward = 'AB' | Range('C', 'D')
    assert forward != backward
    assert forward == Group(Range('A', 'B'), Sequence('CD'), OR=True)
    assert backward == Group(Sequence('AB'), Range('C', 'D'), OR=True)

    forward = Range('A') | 'BCDE'
    backward = 'A' | Range(('B', 'E'))
    assert forward != backward
    assert forward == Group(Range('A'), Sequence('BCDE'), OR=True)
    assert backward == Range('A', ('B', 'E'))

    forward = Range(('A', 'D')) | 'E'
    backward = 'ABCD' | Range('E')
    assert forward != backward
    assert forward == Range(('A', 'E'))
    assert backward == Group(Sequence('ABCD'), Range('E'), OR=True)

    forward = Range(('A', 'C')) | 'DE'
    backward = 'AB' | Range(('C', 'E'))
    assert forward != backward
    assert forward != backward
    assert forward == Group(Range(('A', 'C')), Sequence('DE'), OR=True)
    assert backward == Group(Sequence('AB'), Range(('C', 'E')), OR=True)

def test_range_or_illegal():
    with pytest.raises(TypeError):
        forward = Range('A') | None
    with pytest.raises(TypeError):
        backward = None | Range('A', 'B')
    with pytest.raises(ValueError):
        forward = Range(('A', 'C')) | ''
    with pytest.raises(ValueError):
        backward = '' | Range(('A', 'C'))
    with pytest.raises(TypeError):
        forward = Range('A', 'A', 'A') | 42
    with pytest.raises(TypeError):
        backward = 42 | Range('A', 'A', 'A')
    with pytest.raises(TypeError):
        forward = Range(('A', 'C')) | ('A', 'B', 'C')
    with pytest.raises(TypeError):
        forward = ('A', 'B', 'C') | Range(('A', 'C'))

