from collections.abc import Callable

from .model import (
    Code,
    Document,
    Element,
    Heading,
    Image,
    Input,
    List,
    Metadata,
    Paragraph,
    Shell,
    Table,
)
from .parser import parse_document


INDENT = "  "

_METADATA_FIELDS = (
    "title",
    "subtitle",
    "author",
    "version",
    "date",
    "company",
    "customer",
    "language",
    "theme",
    "revision",
)


def _indent_line(line: str, level: int) -> str:
    if not line:
        return ""

    return f"{INDENT * level}{line}"


def _indent_lines(lines: list[str], level: int) -> list[str]:
    return [_indent_line(line, level) for line in lines]


def _format_metadata(metadata: Metadata) -> str | None:
    lines = ["---"]

    has_values = False

    for field_name in _METADATA_FIELDS:
        value = getattr(metadata, field_name)

        if value is None:
            continue

        lines.append(f"{field_name}: {value}")
        has_values = True

    if not has_values:
        return None

    lines.append("---")
    return "\n".join(lines)


def _format_heading(heading: Heading) -> str:
    return "\n".join(
        [
            heading.level,
            _indent_line(heading.title, 1),
        ]
    )


def _format_paragraph(paragraph: Paragraph) -> str:
    return paragraph.text.strip("\n")


def _format_input(input_: Input) -> str:
    return "\n".join(
        [
            "input",
            _indent_line(input_.path, 1),
        ]
    )


def _format_table(table: Table) -> str:
    lines = [
        "table",
        _indent_line("params", 1),
    ]

    if table.label:
        lines.append(_indent_line(f"label: {table.label}", 2))

    lines.append(_indent_line(f"caption: {table.caption}", 2))

    lines.extend(
        [
            "",
            _indent_line("head", 1),
            _indent_line(" | ".join(table.header), 2),
        ]
    )

    if table.rows:
        lines.extend(
            [
                "",
                _indent_line("body", 1),
                *_indent_lines(
                    [" | ".join(row) for row in table.rows],
                    2,
                ),
            ]
        )

    return "\n".join(lines)


def _format_image(image: Image) -> str:
    lines = [
        "image",
        _indent_line("params", 1),
    ]

    if image.label:
        lines.append(_indent_line(f"label: {image.label}", 2))

    lines.extend(
        [
            _indent_line(f"caption: {image.caption}", 2),
            "",
            _indent_line("file", 1),
            _indent_line(image.file, 2),
        ]
    )

    return "\n".join(lines)


def _format_fenced_body(body: list[str]) -> list[str]:
    return [
        _indent_line("---", 2),
        *_indent_lines(body, 2),
        _indent_line("---", 2),
    ]


def _format_code(code: Code) -> str:
    lines = [
        "code",
        _indent_line("params", 1),
    ]

    if code.label:
        lines.append(_indent_line(f"label: {code.label}", 2))

    if code.caption:
        lines.append(_indent_line(f"caption: {code.caption}", 2))

    lines.extend(
        [
            _indent_line(f"language: {code.language}", 2),
            "",
            _indent_line("body", 1),
            *_format_fenced_body(code.body),
        ]
    )

    return "\n".join(lines)


def _format_list(list_: List) -> str:
    return "\n".join(
        [
            "list",
            _indent_line("params", 1),
            _indent_line(f"type: {list_.type}", 2),
            "",
            _indent_line("body", 1),
            *_format_fenced_body(list_.items),
        ]
    )


def _format_shell(shell: Shell) -> str:
    lines = [
        "shell",
        _indent_line("params", 1),
        _indent_line(f"style: {shell.style}", 2),
    ]

    if shell.title:
        lines.append(_indent_line(f"title: {shell.title}", 2))

    lines.extend(
        [
            "",
            _indent_line("body", 1),
            *_format_fenced_body(shell.body),
        ]
    )

    return "\n".join(lines)


Formatter = Callable[[object], str]

_FORMATTERS: dict[type[object], Formatter] = {
    Heading: lambda value: _format_heading(value),  # type: ignore[arg-type]
    Paragraph: lambda value: _format_paragraph(value),  # type: ignore[arg-type]
    Input: lambda value: _format_input(value),  # type: ignore[arg-type]
    Table: lambda value: _format_table(value),  # type: ignore[arg-type]
    Image: lambda value: _format_image(value),  # type: ignore[arg-type]
    Code: lambda value: _format_code(value),  # type: ignore[arg-type]
    List: lambda value: _format_list(value),  # type: ignore[arg-type]
    Shell: lambda value: _format_shell(value),  # type: ignore[arg-type]
}


def _format_element(element: Element) -> str:
    formatter = _FORMATTERS.get(type(element))

    if formatter is None:
        raise TypeError(f"Unsupported LDL element: {type(element).__name__}")

    return formatter(element)


def format_document(document: Document) -> str:
    parts: list[str] = []

    metadata = _format_metadata(document.metadata)

    if metadata is not None:
        parts.append(metadata)

    parts.extend(_format_element(element) for element in document.elements)

    if not parts:
        return ""

    return "\n\n".join(parts) + "\n"


def format_source(source: str) -> str:
    return format_document(parse_document(source))
