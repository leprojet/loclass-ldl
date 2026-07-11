from loclass_ldl.formatter import format_source


def test_formats_heading_and_paragraph() -> None:
    source = """chapter
       Einführung


Dies ist ein Absatz.
"""

    expected = """chapter
  Einführung

Dies ist ein Absatz.
"""

    assert format_source(source) == expected


def test_formats_manifest_in_canonical_order() -> None:
    source = """---
author: Frank Sieger
title: LDL-Spezifikation
language: de-DE
---

section
    Einführung
"""

    expected = """---
title: LDL-Spezifikation
author: Frank Sieger
language: de-DE
---

section
  Einführung
"""

    assert format_source(source) == expected


def test_formats_input() -> None:
    source = """input
       chapters/introduction.ldl
"""

    expected = """input
  chapters/introduction.ldl
"""

    assert format_source(source) == expected


def test_formats_table() -> None:
    source = """table
  params
       caption: Beispiel
       label: tbl-example
  head
        Name|Alter
  body
          Frank|45
          Lisa|39
"""

    expected = """table
  params
    label: tbl-example
    caption: Beispiel

  head
    Name | Alter

  body
    Frank | 45
    Lisa | 39
"""

    assert format_source(source) == expected


def test_formats_table_without_body() -> None:
    source = """table
  params
    caption: Leere Tabelle
  head
    Name | Wert
"""

    expected = """table
  params
    caption: Leere Tabelle

  head
    Name | Wert
"""

    assert format_source(source) == expected


def test_formats_image() -> None:
    source = """image
  params
      caption: Architektur
      label: fig-architecture
  file
        architecture.png
"""

    expected = """image
  params
    label: fig-architecture
    caption: Architektur

  file
    architecture.png
"""

    assert format_source(source) == expected


def test_formats_code_and_preserves_body_indentation() -> None:
    source = """code
  params
       caption: Python-Beispiel
       language: python
       label: code-example
  body
    ---
    def main():
        print("Hallo")
    ---
"""

    expected = """code
  params
    label: code-example
    caption: Python-Beispiel
    language: python

  body
    ---
    def main():
        print("Hallo")
    ---
"""

    assert format_source(source) == expected


def test_formats_list() -> None:
    source = """list
  params
       type: unordered
  body
    ---
    Eins
    Zwei
    Drei
    ---
"""

    expected = """list
  params
    type: unordered

  body
    ---
    Eins
    Zwei
    Drei
    ---
"""

    assert format_source(source) == expected


def test_formats_shell() -> None:
    source = """shell
  params
       title: Installation
       style: linux
  body
    ---
    uv sync
    uv run pytest
    ---
"""

    expected = """shell
  params
    style: linux
    title: Installation

  body
    ---
    uv sync
    uv run pytest
    ---
"""

    assert format_source(source) == expected


def test_formatter_is_idempotent() -> None:
    source = """---
author: Frank Sieger
title: LDL
---

chapter
      Einführung

table
  params
       caption: Beispiel
  head
       Name|Wert
  body
       Eins|1
"""

    formatted = format_source(source)

    assert format_source(formatted) == formatted


def test_empty_document_remains_empty() -> None:
    assert format_source("") == ""
