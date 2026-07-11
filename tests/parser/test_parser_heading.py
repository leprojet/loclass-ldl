from loclass_ldl.parser import parse_heading


def test_parse_chapter():
    heading = parse_heading("chapter\n  Kapitel 1")
    assert heading.level == "chapter"
    assert heading.title == "Kapitel 1"


def test_parse_section():
    heading = parse_heading("section\n  Motivation")
    assert heading.level == "section"
    assert heading.title == "Motivation"


def test_parse_subsection():
    heading = parse_heading("subsection\n  Parser")
    assert heading.level == "subsection"
    assert heading.title == "Parser"
