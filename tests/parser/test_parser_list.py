import pytest

from loclass_ldl.model import List
from loclass_ldl.parser import parse_list


def test_parse_unordered_list():
    source = """
list
  params
    type: unordered

  body
    ---
    Eins
    Zwei
    Drei
    ---
"""

    result = parse_list(source)

    assert result == List(
        type="unordered",
        items=["Eins", "Zwei", "Drei"],
    )


def test_parse_ordered_list():
    source = """
list
  params
    type: ordered

  body
    ---
    Installation
    Konfiguration
    Test
    ---
"""

    result = parse_list(source)

    assert result == List(
        type="ordered",
        items=["Installation", "Konfiguration", "Test"],
    )


def test_list_requires_valid_type():
    source = """
list
  params
    type: fancy

  body
    ---
    Eins
    ---
"""

    with pytest.raises(ValueError):
        parse_list(source)


def test_list_requires_items():
    source = """
list
  params
    type: unordered

  body
    ---
    ---
"""

    with pytest.raises(ValueError):
        parse_list(source)
