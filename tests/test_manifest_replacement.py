from loclass_ldl import replace_manifest
from loclass_ldl.model import Metadata


def test_replaces_manifest_without_formatting_body() -> None:
    source = """---
title: Alter Titel
---

chapter
  Einführung

table
  params
    caption: Netzwerkports

  head
    Dienst | Port

  body
    HTTP  | 80
"""

    result = replace_manifest(
        source,
        Metadata(
            title="Neuer Titel",
            author="Frank Sieger",
        ),
        {
            "loclass.tlp": {
                "label": "amber",
            }
        },
    )

    assert (
        result
        == """---
title: Neuer Titel
author: Frank Sieger
packages:
  loclass.tlp:
    label: amber
---

chapter
  Einführung

table
  params
    caption: Netzwerkports

  head
    Dienst | Port

  body
    HTTP  | 80
"""
    )


def test_adds_manifest_to_document_without_manifest() -> None:
    source = """chapter
  Einführung
"""

    result = replace_manifest(
        source,
        Metadata(title="Systemkonzept"),
        {},
    )

    assert (
        result
        == """---
title: Systemkonzept
---

chapter
  Einführung
"""
    )


def test_removes_manifest_when_replacement_is_empty() -> None:
    source = """---
title: Temporäres Dokument
---

chapter
  Einführung
"""

    result = replace_manifest(
        source,
        Metadata(),
        {},
    )

    assert (
        result
        == """
chapter
  Einführung
"""
    )
