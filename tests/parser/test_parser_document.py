from loclass_ldl.parser import parse_document
from loclass_ldl.model import Heading, Code, Document, Metadata, List, Paragraph


def test_parse_document_with_multiple_directives():
    source = """
chapter
  Einführung

section
  Beispiel

code
  params
    language: python
    caption: Hello

  body
    ---
    print("Hallo")
    ---
"""

    document = parse_document(source)

    assert document == Document(
        metadata=Metadata(),
        elements=[
            Heading(level="chapter", title="Einführung"),
            Heading(level="section", title="Beispiel"),
            Code(
                label=None,
                caption="Hello",
                language="python",
                body=['print("Hallo")'],
            ),
        ],
    )


def test_parse_list_followed_by_paragraph():
    source = """list
  params
    type: unordered

  body
    ---
    first item
    ---

Paragraph after the list.
"""

    document = parse_document(source)

    assert document.elements == [
        List(
            type="unordered",
            items=["first item"],
        ),
        Paragraph(
            text="Paragraph after the list.",
        ),
    ]
