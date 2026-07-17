"""Parsing and formatting of the LDL document manifest."""

from collections.abc import Mapping

import yaml
from yaml.nodes import MappingNode
from yaml.resolver import BaseResolver

from .model import (
    ManifestValue,
    Metadata,
    PackageConfigurations,
)

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

_ALLOWED_TOP_LEVEL_FIELDS = set(_METADATA_FIELDS) | {"packages"}

_TIMESTAMP_TAG = "tag:yaml.org,2002:timestamp"


class ManifestError(ValueError):
    """Raised when an LDL manifest is invalid."""


class _ManifestLoader(yaml.SafeLoader):
    """Safe YAML loader with unique string mapping keys."""


# Keep dates such as 2026-07-12 as strings.
_ManifestLoader.yaml_implicit_resolvers = {
    first_character: [
        (tag, pattern) for tag, pattern in resolvers if tag != _TIMESTAMP_TAG
    ]
    for first_character, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _construct_unique_mapping(
    loader: _ManifestLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    mapping: dict[str, object] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(
            key_node,
            deep=deep,
        )

        if not isinstance(key, str):
            raise ManifestError("Package configuration keys must be strings.")

        if key in mapping:
            raise ManifestError(f"Duplicate package configuration key: {key!r}")

        mapping[key] = loader.construct_object(
            value_node,
            deep=deep,
        )

    return mapping


_ManifestLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class _ManifestDumper(yaml.SafeDumper):
    """Canonical YAML dumper for package configuration."""

    def increase_indent(
        self,
        flow: bool = False,
        indentless: bool = False,
    ) -> None:
        super().increase_indent(
            flow=flow,
            indentless=False,
        )

    def ignore_aliases(self, data: object) -> bool:
        return True


def _normalize_manifest_value(
    value: object,
    *,
    path: str,
) -> ManifestValue:
    if value is None or isinstance(
        value,
        (str, bool, int, float),
    ):
        return value

    if isinstance(value, list):
        return [
            _normalize_manifest_value(
                item,
                path=f"{path}[{index}]",
            )
            for index, item in enumerate(value)
        ]

    if isinstance(value, Mapping):
        normalized: dict[str, ManifestValue] = {}

        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ManifestError(f"Manifest mapping key at {path} must be a string.")

            normalized[key] = _normalize_manifest_value(
                nested_value,
                path=f"{path}.{key}",
            )

        return normalized

    raise ManifestError(f"Unsupported manifest value at {path}: {type(value).__name__}")


def _parse_package_configurations(
    lines: list[str],
) -> PackageConfigurations:
    if not lines:
        return {}

    dedented_lines: list[str] = []

    for line in lines:
        if not line.strip():
            dedented_lines.append("")
            continue

        if not line.startswith("  "):
            raise ManifestError(
                "Entries below 'packages:' must be indented by at least two spaces."
            )

        dedented_lines.append(line[2:])

    source = "\n".join(dedented_lines)

    try:
        loaded = yaml.load(
            source,
            Loader=_ManifestLoader,
        )
    except ManifestError:
        raise
    except yaml.YAMLError as exc:
        raise ManifestError(f"Invalid packages section: {exc}") from exc

    if loaded is None:
        return {}

    if not isinstance(loaded, Mapping):
        raise ManifestError("The 'packages' section must be a mapping.")

    configurations: PackageConfigurations = {}

    for package_id, raw_configuration in loaded.items():
        if not isinstance(package_id, str):
            raise ManifestError("Package IDs must be strings.")

        if raw_configuration is None:
            raise ManifestError(
                f"Configuration for package {package_id!r} "
                "must be a mapping; use '{}'."
            )

        if not isinstance(raw_configuration, Mapping):
            raise ManifestError(
                f"Configuration for package {package_id!r} must be a mapping."
            )

        normalized = _normalize_manifest_value(
            raw_configuration,
            path=f"packages.{package_id}",
        )

        if not isinstance(normalized, dict):
            raise ManifestError(
                f"Configuration for package {package_id!r} must be a mapping."
            )

        configurations[package_id] = normalized

    return configurations


def parse_manifest(
    source: str,
) -> tuple[Metadata, PackageConfigurations, str]:
    """Parse the optional root manifest and return the remaining body."""

    lines = source.splitlines()

    start = 0

    while start < len(lines) and not lines[start].strip():
        start += 1

    if start >= len(lines) or lines[start].strip() != "---":
        return Metadata(), {}, source

    metadata_values: dict[str, str] = {}
    package_lines: list[str] = []

    packages_seen = False
    inside_packages = False

    index = start + 1

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not line.startswith(" ") and stripped == "---":
            body = "\n".join(lines[index + 1 :])

            package_configurations = _parse_package_configurations(package_lines)

            return (
                Metadata(**metadata_values),
                package_configurations,
                body,
            )

        if not stripped:
            if inside_packages:
                package_lines.append("")

            index += 1
            continue

        if line.startswith(" "):
            if not inside_packages:
                raise ManifestError(f"Unexpected indentation in manifest: {line}")

            package_lines.append(line)
            index += 1
            continue

        inside_packages = False

        if ":" not in line:
            raise ManifestError(f"Invalid manifest line: {line}")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key not in _ALLOWED_TOP_LEVEL_FIELDS:
            raise ManifestError(f"Unknown metadata field: {key}")

        if key == "packages":
            if packages_seen:
                raise ManifestError("Duplicate manifest field: packages")

            if value:
                raise ManifestError("'packages' must be a nested mapping.")

            packages_seen = True
            inside_packages = True
            index += 1
            continue

        if key in metadata_values:
            raise ManifestError(f"Duplicate metadata field: {key}")

        metadata_values[key] = value
        index += 1

    raise ManifestError("Manifest must end with '---'.")


def format_manifest(
    metadata: Metadata,
    package_configurations: PackageConfigurations,
) -> str | None:
    """Format document metadata and package configuration canonically."""

    lines = ["---"]
    has_values = False

    for field_name in _METADATA_FIELDS:
        value = getattr(metadata, field_name)

        if value is None:
            continue

        lines.append(f"{field_name}: {value}")
        has_values = True

    if package_configurations:
        lines.append("packages:")

        package_yaml = yaml.dump(
            package_configurations,
            Dumper=_ManifestDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=True,
            width=88,
        ).rstrip()

        lines.extend(f"  {line}" if line else "" for line in package_yaml.splitlines())

        has_values = True

    if not has_values:
        return None

    lines.append("---")
    return "\n".join(lines)


def _detect_newline(source: str) -> str:
    if "\r\n" in source:
        return "\r\n"

    return "\n"


def _body_after_manifest(source: str) -> tuple[bool, str]:
    """Return whether a manifest exists and the unchanged document body."""

    lines = source.splitlines(keepends=True)

    start = 0

    while start < len(lines) and not lines[start].strip():
        start += 1

    if start >= len(lines) or lines[start].strip() != "---":
        return False, source

    for index in range(start + 1, len(lines)):
        line = lines[index]

        if not line.startswith((" ", "\t")) and line.strip() == "---":
            return True, "".join(lines[index + 1 :])

    raise ManifestError("Manifest must end with '---'.")


def replace_manifest(
    source: str,
    metadata: Metadata,
    package_configurations: PackageConfigurations,
) -> str:
    """Replace the root manifest while preserving the LDL body."""

    # Validate an existing manifest before replacing it.
    parse_manifest(source)

    had_manifest, body = _body_after_manifest(source)
    manifest = format_manifest(
        metadata,
        package_configurations,
    )

    if manifest is None:
        return body if had_manifest else source

    newline = _detect_newline(source)
    manifest = manifest.replace("\n", newline)

    if had_manifest:
        return manifest + newline + body

    if not source:
        return manifest + newline

    return manifest + newline + newline + source
