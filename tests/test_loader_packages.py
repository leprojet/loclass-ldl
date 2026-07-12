from loclass_ldl import load_document


def test_loader_preserves_root_package_configurations(
    tmp_path,
) -> None:
    root = tmp_path / "main.ldl"
    child = tmp_path / "child.ldl"

    root.write_text(
        """---
title: Sicherheitsbericht
packages:
  loclass.tlp:
    label: amber
---

input
  child.ldl
""",
        encoding="utf-8",
    )

    child.write_text(
        """chapter
  Inhalt
""",
        encoding="utf-8",
    )

    document = load_document(root)

    assert document.package_configurations == {
        "loclass.tlp": {
            "label": "amber",
        }
    }

    assert len(document.elements) == 1
