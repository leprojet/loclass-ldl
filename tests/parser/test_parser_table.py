import pytest

from loclass_ldl import parse_table


def test_parse_table():
    source = """
table
  params
    label: tab:ports
    caption: Netzwerkports

  head
    Dienst | Port | Protokoll

  body
    HTTP  | 80  | TCP
    HTTPS | 443 | TCP
    DNS   | 53  | UDP
"""

    table = parse_table(source)

    assert table.label == "tab:ports"
    assert table.caption == "Netzwerkports"
    assert table.header == ["Dienst", "Port", "Protokoll"]
    assert table.rows == [
        ["HTTP", "80", "TCP"],
        ["HTTPS", "443", "TCP"],
        ["DNS", "53", "UDP"],
    ]


def test_table_requires_caption():
    source = """
table
  params
    label: tab:ports

  head
    Dienst | Port

  body
    HTTP | 80
"""

    with pytest.raises(ValueError, match="caption"):
        parse_table(source)


def test_table_requires_head():
    source = """
table
  params
    caption: Netzwerkports

  body
    HTTP | 80
"""

    with pytest.raises(ValueError, match="head"):
        parse_table(source)


def test_table_row_length_must_match_header():
    source = """
table
  params
    caption: Netzwerkports

  head
    Dienst | Port

  body
    HTTP | 80 | TCP
"""

    with pytest.raises(ValueError, match="expected 2"):
        parse_table(source)
