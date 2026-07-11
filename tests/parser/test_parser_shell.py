import pytest

from loclass_ldl.model import Shell
from loclass_ldl.parser import parse_shell


def test_parse_linux_shell():
    source = """
shell
  params
    style: linux
    title: Server

  body
    ---
    uv run pytest
    docker ps
    ---
"""

    shell = parse_shell(source)

    assert shell == Shell(
        style="linux",
        title="Server",
        body=[
            "uv run pytest",
            "docker ps",
        ],
    )


def test_shell_requires_valid_style():
    source = """
shell
  params
    style: amiga

  body
    ---
    dir
    ---
"""

    with pytest.raises(ValueError):
        parse_shell(source)
