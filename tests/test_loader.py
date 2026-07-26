from loclass_ldl.loader import LdlInputError, load_document
from loclass_ldl.model import Document, Heading, Paragraph

import pytest


def test_load_document_without_input(tmp_path):
    source = tmp_path / "main.ldl"

    source.write_text(
        """chapter
  Hauptdokument

Das ist normaler Text.
""",
        encoding="utf-8",
    )

    document = load_document(source)

    assert document == Document(
        elements=[
            Heading(level="chapter", title="Hauptdokument"),
            Paragraph(text="Das ist normaler Text."),
        ],
    )


def test_load_document_accepts_input_without_manifest(tmp_path):
    main = tmp_path / "main.ldl"
    child = tmp_path / "child.ldl"

    main.write_text(
        """chapter
  Hauptdokument

input
  child.ldl
""",
        encoding="utf-8",
    )

    child.write_text(
        """section
  Eingebunden

Das kommt aus der Kinddatei.
""",
        encoding="utf-8",
    )

    document = load_document(main)

    assert document == Document(
        elements=[
            Heading(level="chapter", title="Hauptdokument"),
            Heading(level="section", title="Eingebunden"),
            Paragraph(text="Das kommt aus der Kinddatei."),
        ],
    )


def test_load_document_with_missing_input(tmp_path):
    main = tmp_path / "main.ldl"

    main.write_text(
        """input
  missing.ldl
""",
        encoding="utf-8",
    )

    with pytest.raises(LdlInputError, match="LDL input file not found"):
        load_document(main)


def test_load_document_detects_circular_input(tmp_path):
    a = tmp_path / "a.ldl"
    b = tmp_path / "b.ldl"

    a.write_text(
        """input
  b.ldl
""",
        encoding="utf-8",
    )

    b.write_text(
        """input
  a.ldl
""",
        encoding="utf-8",
    )

    with pytest.raises(LdlInputError, match="Circular LDL input detected"):
        load_document(a)


def test_load_document_rejects_manifest_in_input_first_line(tmp_path):
    main = tmp_path / "main.ldl"
    child = tmp_path / "child.ldl"

    main.write_text(
        """input
  child.ldl
""",
        encoding="utf-8",
    )

    child.write_text(
        """---
title: Kinddokument
---

chapter
  Darf nicht sein
""",
        encoding="utf-8",
    )

    with pytest.raises(
        LdlInputError, match="Manifest is only allowed in the root LDL document"
    ):
        load_document(main)


@pytest.mark.parametrize("leading_blank_lines", [1, 3])
def test_load_document_rejects_manifest_in_input_after_leading_blank_lines(
    tmp_path,
    leading_blank_lines,
):
    main = tmp_path / "main.ldl"
    child = tmp_path / "child.ldl"

    main.write_text(
        """input
  child.ldl
""",
        encoding="utf-8",
    )

    child.write_text(
        "\n" * leading_blank_lines
        + """---
title: Kinddokument
---

chapter
  Darf nicht sein
""",
        encoding="utf-8",
    )

    with pytest.raises(
        LdlInputError, match="Manifest is only allowed in the root LDL document"
    ):
        load_document(main)
