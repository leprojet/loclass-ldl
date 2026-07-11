from loclass_ldl.inline import lex_inline
from loclass_ldl.model import Bold, Italic, Text, Underline


def test_lex_plain_text():
    assert lex_inline("Hello") == [
        Text("Hello"),
    ]
    assert lex_inline("/italic/") == [
        Italic("italic"),
    ]


def test_lex_bold():
    assert lex_inline("Hello *World*!") == [
        Text("Hello "),
        Bold("World"),
        Text("!"),
    ]


def test_lex_underline():
    assert lex_inline("+underline+") == [
        Underline("underline"),
    ]
