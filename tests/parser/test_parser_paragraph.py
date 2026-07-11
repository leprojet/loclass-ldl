from loclass_ldl.model import Document, Paragraph
from loclass_ldl.parser import parse_document


def test_parse_paragraph():
    document = parse_document("Dies ist normaler Fließtext.")

    assert document == Document(
        elements=[
            Paragraph(text="Dies ist normaler Fließtext."),
        ],
    )
