# loclass-ldl

`loclass-ldl` provides the backend-neutral implementation of the
**loclass document language (LDL)**.

It parses LDL source files into a neutral document model that can be consumed
by converters and output backends without depending on LaTeX, ODT, or another
rendering format.

## Role in the loclass ecosystem

The loclass ecosystem is split into three repositories:

| Repository | Purpose |
| --- | --- |
| `loclass-ldl` | LDL specification, parsing, loading, formatting, and document model |
| `loclass-base` | Conversion pipeline, CLI, and output backends |
| `loclass-starter` | Reference project and starter structure for loclass documents |

The processing flow is:

```text
LDL source
    ↓
loclass-ldl
    ↓
neutral Document model
    ↓
loclass-base converter
    ↓
LaTeX, ODT, or another backend
```

## Responsibilities

`loclass-ldl` contains the language-level functionality:

- manifest parsing
- block parsing
- inline tokenization
- document model definitions
- recursive `input` resolution
- path handling for included files
- cycle detection
- source formatting
- block and inline registries
- validation and readable parse errors

Rendering is deliberately outside the scope of this package.

## LDL composition

A document starts with one manifest followed by document content:

```ldl
---
title: Example document
author: Frank Sieger
language: en
version: 0.1.0
---

chapter
  Introduction

This document is written in LDL.

input
  content/details.ldl
```

Included files contain document content only:

```ldl
section
  Details

Run the test suite with __cmd{uv run pytest}.
```

Paths used by `input` are resolved relative to the file containing the
directive.

A document has exactly one manifest: the manifest belongs to the root file,
not to included files.

## Inline elements

LDL supports inline elements such as:

```ldl
Run __cmd{uv run pytest}.

Press __keys{Ctrl+Alt+T}.

Open __url{https://example.org/docs}.

The value is __code{None}.
```

Inline elements are represented in the neutral document model and interpreted
later by the selected output backend.

## Development

Install the project dependencies:

```bash
uv sync
```

Run the tests:

```bash
uv run pytest
```

Run the static checks:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

## Design principles

- LDL describes document structure, not output formatting.
- Source composition is resolved before rendering.
- Backends receive a complete neutral document.
- Language functionality remains independent of output formats.
- Errors should identify the relevant source file and location.
- The canonical formatter should produce stable LDL source.

## Version

The current development milestone is `0.1.0`.
