from .manifest import parse_manifest

from .model import (
    Code,
    Document,
    Element,
    Heading,
    Paragraph,
    Image,
    Input,
    List,
    Shell,
    Table,
)


def _normalize_lines(source: str) -> list[str]:
    return [line.rstrip() for line in source.splitlines() if line.strip()]


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.split("|")]


def _parse_param_line(line: str) -> tuple[str, str]:
    stripped = line.strip()

    if ":" not in stripped:
        raise ValueError(f"Invalid parameter line: {line}")

    key, value = stripped.split(":", 1)
    return key.strip(), value.strip()


def _parse_common_params(params: dict[str, str]) -> tuple[str | None, str | None]:
    label = params.get("label") or None
    caption = params.get("caption") or None
    return label, caption


def _parse_fenced_body(lines: list[str]) -> list[str]:
    if not lines:
        raise ValueError("Missing body.")

    if lines[0].strip() != "---":
        raise ValueError("Body must start with '---'.")

    if lines[-1].strip() != "---":
        raise ValueError("Body must end with '---'.")

    body = lines[1:-1]

    return [line[4:] if line.startswith("    ") else line for line in body]


def parse_table(source: str) -> Table:
    lines = _normalize_lines(source)

    if not lines or lines[0].strip() != "table":
        raise ValueError("LDL table block must start with 'table'.")

    params: dict[str, str] = {}
    header: list[str] | None = None
    rows: list[list[str]] = []

    section: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        indent = _indent(line)

        if indent == 2 and stripped in {"params", "head", "body"}:
            section = stripped
            continue

        if section == "params":
            key, value = _parse_param_line(line)

            if key not in {"label", "caption"}:
                raise ValueError(f"Unknown table parameter: {key}")

            params[key] = value

        elif section == "head":
            header = _split_cells(stripped)

        elif section == "body":
            rows.append(_split_cells(stripped))

        else:
            raise ValueError(f"Line outside known table section: {line}")

    label, caption = _parse_common_params(params)

    if not caption:
        raise ValueError("Table requires a caption.")

    if not header:
        raise ValueError("Table requires a head section.")

    column_count = len(header)

    for row in rows:
        if len(row) != column_count:
            raise ValueError(
                f"Table row has {len(row)} cells, expected {column_count}: {row}"
            )

    return Table(
        label=label,
        caption=caption,
        header=header,
        rows=rows,
    )


def parse_image(source: str) -> Image:
    lines = _normalize_lines(source)

    if not lines or lines[0].strip() != "image":
        raise ValueError("LDL image block must start with 'image'.")

    params: dict[str, str] = {}
    file: str | None = None

    section: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        indent = _indent(line)

        if indent == 2 and stripped in {"params", "file"}:
            section = stripped
            continue

        if section == "params":
            key, value = _parse_param_line(line)

            if key not in {"label", "caption"}:
                raise ValueError(f"Unknown image parameter: {key}")

            params[key] = value

        elif section == "file":
            file = stripped

        else:
            raise ValueError(f"Line outside known image section: {line}")

    label, caption = _parse_common_params(params)

    if not caption:
        raise ValueError("Image requires a caption.")

    if not file:
        raise ValueError("Image requires a file.")

    return Image(
        label=label,
        caption=caption,
        file=file,
    )


def parse_code(source: str) -> Code:
    lines = [line.rstrip() for line in source.splitlines()]

    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines or lines[0].strip() != "code":
        raise ValueError("LDL code block must start with 'code'.")

    params: dict[str, str] = {}
    body_lines: list[str] = []

    section: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        indent = _indent(line)

        if not stripped and section != "body":
            continue

        if indent == 2 and stripped in {"params", "body"}:
            section = stripped
            continue

        if section == "params":
            key, value = _parse_param_line(line)

            if key not in {"label", "caption", "language"}:
                raise ValueError(f"Unknown code parameter: {key}")

            params[key] = value

        elif section == "body":
            body_lines.append(line)

        else:
            raise ValueError(f"Line outside known code section: {line}")

    label, caption = _parse_common_params(params)
    language = params.get("language")
    body = _parse_fenced_body(body_lines)

    if not language:
        raise ValueError("Code requires a language.")

    if not body:
        raise ValueError("Code requires a body.")

    return Code(
        label=label,
        caption=caption,
        language=language,
        body=body,
    )


def parse_heading(source: str) -> Heading:
    lines = _normalize_lines(source)

    if not lines:
        raise ValueError("LDL heading block is empty.")

    level = lines[0].strip()

    if level not in {"chapter", "section", "subsection"}:
        raise ValueError(f"Unsupported heading level: {level}")

    if len(lines) < 2:
        raise ValueError("Heading requires a title.")

    title = lines[1].strip()

    if not title:
        raise ValueError("Heading requires a title.")

    return Heading(level=level, title=title)


def parse_input(source: str) -> Input:
    lines = _normalize_lines(source)

    if not lines or lines[0].strip() != "input":
        raise ValueError("LDL input block must start with 'input'.")

    if len(lines) < 2:
        raise ValueError("Input requires a path.")

    path = lines[1].strip()

    if not path:
        raise ValueError("Input requires a path.")

    return Input(path=path)


def _directive_name(line: str) -> str:
    return line.strip()


def _split_blocks(source: str) -> list[str]:
    known_directives = {
        "chapter",
        "section",
        "subsection",
        "input",
        "table",
        "image",
        "code",
        "list",
        "shell",
    }

    heading_directives = {
        "chapter",
        "section",
        "subsection",
    }

    single_value_directives = heading_directives | {"input"}

    lines = [line.rstrip() for line in source.splitlines()]
    blocks: list[str] = []

    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        is_directive = not line.startswith(" ") and stripped in known_directives

        if is_directive:
            directive = stripped

            if directive in single_value_directives:
                block = [line]

                if i + 1 < len(lines):
                    block.append(lines[i + 1])
                    i += 2
                else:
                    i += 1

                blocks.append("\n".join(block).strip("\n"))
                continue

            block = [line]
            i += 1

            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()

                next_starts_top_level_block = bool(
                    next_stripped
                ) and not next_line.startswith(" ")

                if next_starts_top_level_block:
                    break

                block.append(next_line)
                i += 1

            blocks.append("\n".join(block).strip("\n"))
            continue

        raw_block: list[str] = []

        while i < len(lines):
            next_line = lines[i]
            next_stripped = next_line.strip()

            next_is_directive = (
                bool(next_stripped)
                and not next_line.startswith(" ")
                and next_stripped in known_directives
            )

            if next_is_directive:
                break

            raw_block.append(next_line)
            i += 1

        raw_text = "\n".join(raw_block).strip("\n")

        if raw_text:
            blocks.append(raw_text)

    return blocks


def parse_document(source: str) -> Document:
    from .registry import PARSERS

    metadata, package_configurations, body = parse_manifest(source)
    elements: list[Element] = []

    for block in _split_blocks(body):
        if not block.strip():
            continue

        first_line = block.splitlines()[0]
        directive = _directive_name(first_line)

        if directive in PARSERS:
            elements.append(PARSERS[directive](block))
        else:
            elements.append(Paragraph(text=block))

    return Document(
        metadata=metadata,
        elements=elements,
        package_configurations=package_configurations,
    )


def parse_list(source: str) -> List:
    lines = [line.rstrip() for line in source.splitlines()]

    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines or lines[0].strip() != "list":
        raise ValueError("LDL list block must start with 'list'.")

    params: dict[str, str] = {}
    body_lines: list[str] = []

    section: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        indent = _indent(line)

        if not stripped and section != "body":
            continue

        if indent == 2 and stripped in {"params", "body"}:
            section = stripped
            continue

        if section == "params":
            key, value = _parse_param_line(line)

            if key != "type":
                raise ValueError(f"Unknown list parameter: {key}")

            params[key] = value

        elif section == "body":
            body_lines.append(line)

        else:
            raise ValueError(f"Line outside known list section: {line}")

    list_type = params.get("type")

    if list_type not in {"unordered", "ordered"}:
        raise ValueError("List requires type 'unordered' or 'ordered'.")

    items = [item for item in _parse_fenced_body(body_lines) if item.strip()]

    if not items:
        raise ValueError("List requires at least one item.")

    return List(type=list_type, items=items)


def parse_shell(source: str) -> Shell:
    lines = _normalize_lines(source)

    if not lines or lines[0].strip() != "shell":
        raise ValueError("LDL shell block must start with 'shell'.")

    params: dict[str, str] = {}
    body_lines: list[str] = []

    section: str | None = None

    for line in lines[1:]:
        stripped = line.strip()

        if not stripped and section != "body":
            continue

        indent = _indent(line)

        if indent == 2 and stripped in {"params", "body"}:
            section = stripped
            continue

        if section == "params":
            key, value = _parse_param_line(line)
            params[key] = value

        elif section == "body":
            body_lines.append(line)

    style = params.get("style")

    if style not in {"linux", "windows", "macos"}:
        raise ValueError("Invalid shell style.")

    body = _parse_fenced_body(body_lines)

    return Shell(
        style=style,
        title=params.get("title"),
        body=body,
    )
