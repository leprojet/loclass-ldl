# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic
Versioning.

## [0.1.0] - 2026-07-11

### Added

- Backend-neutral LDL document model.
- Manifest and block parsing.
- Inline element lexer and registry.
- Recursive `input` resolution.
- Relative path handling for included files.
- Circular include detection.
- Canonical LDL source formatter.
- Block and inline registries.
- Validation with source-aware error reporting.
- Test coverage for parsing, loading, formatting, and document composition.

### Changed

- Separated the LDL language layer from conversion and rendering.
- Moved source composition into the LDL loader.
- Ensured output backends receive a complete neutral document.

### Removed

- Obsolete `Raw` document element.
- Rendering responsibilities from the LDL package.
