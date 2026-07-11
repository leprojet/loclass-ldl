from .model import (
    Bold,
    Cmd,
    InlineCode,
    Italic,
    Keys,
    Path,
    Strike,
    Text,
    Underline,
    Url,
)

INLINE_MARKERS = {
    "--": Strike,
    "*": Bold,
    "/": Italic,
    "+": Underline,
}

BRACE_DIRECTIVES = {
    "__path": Path,
    "__cmd": Cmd,
    "__keys": Keys,
    "__url": Url,
    "__code": InlineCode,
}


def _find_marker_at(text: str, position: int) -> str | None:
    for marker in INLINE_MARKERS:
        if text.startswith(marker, position):
            return marker

    return None


def _find_brace_directive_at(text: str, position: int) -> str | None:
    for directive in BRACE_DIRECTIVES:
        if text.startswith(directive + "{", position):
            return directive

    return None


def lex_inline(text: str) -> list[object]:
    tokens: list[object] = []
    buffer: list[str] = []

    i = 0

    while i < len(text):
        directive = _find_brace_directive_at(text, i)

        if directive is not None:
            if buffer:
                tokens.append(Text("".join(buffer)))
                buffer = []

            start = i + len(directive) + 1
            end = text.find("}", start)

            if end == -1:
                buffer.append(text[i])
                i += 1
                continue

            content = text[start:end]
            token_class = BRACE_DIRECTIVES[directive]
            tokens.append(token_class(content))

            i = end + 1
            continue

        marker = _find_marker_at(text, i)

        if marker is not None:
            if buffer:
                tokens.append(Text("".join(buffer)))
                buffer = []

            end = text.find(marker, i + len(marker))

            if end == -1:
                buffer.append(marker)
                i += len(marker)
                continue

            content = text[i + len(marker) : end]
            token_class = INLINE_MARKERS[marker]
            tokens.append(token_class(content))

            i = end + len(marker)
            continue

        buffer.append(text[i])
        i += 1

    if buffer:
        tokens.append(Text("".join(buffer)))

    return tokens
