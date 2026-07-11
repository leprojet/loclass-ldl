from collections.abc import Callable

from .model import Element
from .parser import (
    parse_code,
    parse_heading,
    parse_image,
    parse_input,
    parse_list,
    parse_shell,
    parse_table,
)

Parser = Callable[[str], Element]

PARSERS: dict[str, Parser] = {
    "chapter": parse_heading,
    "section": parse_heading,
    "subsection": parse_heading,
    "table": parse_table,
    "image": parse_image,
    "input": parse_input,
    "code": parse_code,
    "list": parse_list,
    "shell": parse_shell,
}
