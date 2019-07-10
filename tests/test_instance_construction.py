import pytest

from model._klean import Abstract, Group, Literal, Range, Sequence, Quantification
from model.representations import LowerAscii, UpperAscii, LineEnd, Whitespace

def test_building():
    colors = Group(Sequence('blue'), Sequence('green'), Sequence('orange'),
                   Sequence('red'), Sequence('violet'), Sequence('yellow'),
                   OR=True, repetition=Quantification(min=0, max=1))
    assert str(colors) == '(blue<OR>green<OR>orange<OR>red<OR>violet<OR>yellow)<0,1GREATEST>'

    sizes = Group(Sequence('huge'), Sequence('large'), Sequence('medium'),
                  Sequence('small'), Sequence('tiny'), OR=True,
                  repetition=Quantification(min=0, max=1))
    assert str(sizes) == '(huge<OR>large<OR>medium<OR>small<OR>tiny)<0,1GREATEST>'

    positions = Group(Sequence('first'), Sequence('last'), Sequence('second'), Sequence('third'), OR=True)
    assert str(positions) == '(first<OR>last<OR>second<OR>third)<1,1GREATEST>'

    noun = Group(UpperAscii(), Group(LowerAscii(), repetition=Quantification(min=0, max=0)))
    assert str(noun) == r'({A,Z}({a,z})<0,GREATEST>)<1,1GREATEST>'

    spacing = Group(Whitespace(), repetition=Quantification(min=1, max=0))
    assert str(spacing) == r'(<SPACE>)<1,GREATEST>'

    entry = Group(positions, spacing, sizes, spacing, colors, spacing, noun)

    listing = Group(Group(entry, LineEnd(), repetition=Quantification(min=3)), entry)
