import pytest

from loclass_ldl import ManifestError
from loclass_ldl.formatter import format_source
from loclass_ldl.parser import parse_document


def test_parses_package_configurations() -> None:
    source = """---
title: Sicherheitsbericht
packages:
  loclass.tlp:
    label: amber+strict
    notice: true
  example.references:
    groups:
      - internal
      - external
    maximum: 12
---

chapter
  Einführung
"""

    document = parse_document(source)

    assert document.metadata.title == "Sicherheitsbericht"

    assert document.package_configurations == {
        "loclass.tlp": {
            "label": "amber+strict",
            "notice": True,
        },
        "example.references": {
            "groups": [
                "internal",
                "external",
            ],
            "maximum": 12,
        },
    }


def test_document_without_packages_uses_empty_mapping() -> None:
    document = parse_document(
        """---
title: Einfaches Dokument
---

Ein Absatz.
"""
    )

    assert document.package_configurations == {}


def test_metadata_may_follow_packages_section() -> None:
    document = parse_document(
        """---
packages:
  loclass.tlp:
    label: green
title: Nach dem Paket
---
"""
    )

    assert document.metadata.title == "Nach dem Paket"
    assert document.package_configurations == {
        "loclass.tlp": {
            "label": "green",
        }
    }


def test_package_configuration_must_be_mapping() -> None:
    with pytest.raises(
        ManifestError,
        match=("Configuration for package 'loclass.tlp' must be a mapping"),
    ):
        parse_document(
            """---
packages:
  loclass.tlp: amber
---
"""
        )


def test_empty_package_requires_explicit_mapping() -> None:
    with pytest.raises(
        ManifestError,
        match=r"use '\{\}'",
    ):
        parse_document(
            """---
packages:
  loclass.example:
---
"""
        )


def test_duplicate_package_id_is_rejected() -> None:
    with pytest.raises(
        ManifestError,
        match=("Duplicate package configuration key: 'loclass.tlp'"),
    ):
        parse_document(
            """---
packages:
  loclass.tlp:
    label: amber
  loclass.tlp:
    label: green
---
"""
        )


def test_packages_must_be_nested_mapping() -> None:
    with pytest.raises(
        ManifestError,
        match="'packages' must be a nested mapping",
    ):
        parse_document(
            """---
packages: loclass.tlp
---
"""
        )


def test_formatter_writes_canonical_package_manifest() -> None:
    source = """---
packages:
  loclass.tlp: {notice: true, label: amber}
title: Sicherheitsbericht
---
"""

    expected = """---
title: Sicherheitsbericht
packages:
  loclass.tlp:
    label: amber
    notice: true
---
"""

    assert format_source(source) == expected


def test_package_manifest_formatting_is_idempotent() -> None:
    source = """---
title: Sicherheitsbericht
packages:
  loclass.tlp:
    notice: true
    label: amber
  example.references:
    groups:
      - internal
      - external
---
"""

    formatted = format_source(source)

    assert format_source(formatted) == formatted
