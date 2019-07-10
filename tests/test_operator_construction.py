import pytest

from model._klean import Abstract, Group, Literal, Range, Sequence, Quantification
from model.representations import Decimal, StringEnd, StringStart, Whitespace, Word
from resolvers.python import format

def test_and():
    exp = StringStart() & 'Title'
    assert format(exp) == r'\ATitle'
    exp &= Group(Whitespace(), repetition=Quantification(min=0, max=0)) & ':' & Word()
    assert format(exp) == r'(\ATitle(((\s)*:)\w))'
    exp &= '\n'
    assert format(exp) == '((\ATitle(((\s)*:)\w))\\\n)'
    exp &= Group(Whitespace(), repetition=Quantification(min=1, max=0)) & 'H' & 'e' & 'a' & 'd' & 'e' & 'r'
    assert format(exp) == '(((\ATitle(((\s)*:)\w))\\\n)(((((((\s)+H)e)a)d)e)r))'
    exp &= StringEnd()
    assert format(exp) == '((((\ATitle(((\s)*:)\w))\\\n)(((((((\s)+H)e)a)d)e)r))\Z)'
    assert str(exp) == '((((<SOS>Title(((<SPACE>)<0,GREATEST>:)<1,1GREATEST><WORD>)<1,1GREATEST>)<1,1GREATEST>\n)<1,1GREATEST>(((((((<SPACE>)<1,GREATEST>H)<1,1GREATEST>e)<1,1GREATEST>a)<1,1GREATEST>d)<1,1GREATEST>e)<1,1GREATEST>r)<1,1GREATEST>)<1,1GREATEST><EOS>)<1,1GREATEST>'

def test_or():
    exp = Group(Literal('+'), Literal('-'), OR=True, repetition=Quantification(min=0, max=1))
    assert format(exp) == r'(\+|\-)?'
    exp |= Decimal() | Group(Decimal(), Literal('.'), Decimal())
    assert format(exp) == r'((\+|\-)?|(\d|(\d\.\d)))'
    assert str(exp) == "((+<OR>-)<0,1GREATEST><OR>(<D><OR>(<D>.<D>)<1,1GREATEST>)<1,1GREATEST>)<1,1GREATEST>"
