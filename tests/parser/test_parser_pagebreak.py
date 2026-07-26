import pytest

from loclass_ldl.model import Document, PageBreak, Paragraph
from loclass_ldl.parser import parse_document, parse_pagebreak


def test_parse_pagebreak() -> None:
    assert parse_pagebreak("pagebreak") == PageBreak()


def test_parse_pagebreak_rejects_content() -> None:
    with pytest.raises(
        ValueError,
        match="must contain only 'pagebreak'",
    ):
        parse_pagebreak(
            """pagebreak
  unexpected
"""
        )


def test_parse_document_keeps_paragraphs_around_pagebreak() -> None:
    source = """Paragraph before.

pagebreak

Paragraph after.
"""

    assert parse_document(source) == Document(
        elements=[
            Paragraph(text="Paragraph before."),
            PageBreak(),
            Paragraph(text="Paragraph after."),
        ],
    )
