from dataclasses import dataclass, field


@dataclass(frozen=True)
class Table:
    label: str | None
    caption: str
    header: list[str]
    rows: list[list[str]] = field(default_factory=list)


@dataclass(frozen=True)
class Image:
    label: str | None
    caption: str
    file: str


@dataclass(frozen=True)
class Code:
    label: str | None
    caption: str | None
    language: str
    body: list[str]


@dataclass(frozen=True)
class Heading:
    level: str
    title: str


@dataclass(frozen=True)
class List:
    type: str
    items: list[str]


@dataclass(frozen=True)
class Shell:
    style: str
    title: str | None
    body: list[str]


@dataclass(frozen=True)
class Text:
    text: str


@dataclass(frozen=True)
class Bold:
    text: str


@dataclass(frozen=True)
class Italic:
    text: str


@dataclass(frozen=True)
class Underline:
    text: str


@dataclass(frozen=True)
class Strike:
    text: str


@dataclass(frozen=True)
class Path:
    text: str


@dataclass(frozen=True)
class Cmd:
    text: str


@dataclass(frozen=True)
class Keys:
    text: str


@dataclass(frozen=True)
class Url:
    text: str


@dataclass(frozen=True)
class InlineCode:
    text: str


@dataclass(frozen=True)
class Input:
    path: str


@dataclass(frozen=True)
class PageBreak:
    pass


@dataclass(frozen=True)
class Paragraph:
    text: str


@dataclass(frozen=True)
class Metadata:
    title: str | None = None
    subtitle: str | None = None
    author: str | None = None
    version: str | None = None
    date: str | None = None
    company: str | None = None
    customer: str | None = None
    language: str | None = None
    theme: str | None = None
    revision: str | None = None


type ManifestScalar = str | int | float | bool | None
type ManifestValue = ManifestScalar | list[ManifestValue] | dict[str, ManifestValue]
type PackageConfiguration = dict[str, ManifestValue]
type PackageConfigurations = dict[str, PackageConfiguration]


Element = Heading | Paragraph | Input | PageBreak | Table | Image | Code | List | Shell


@dataclass(frozen=True)
class Document:
    metadata: Metadata = field(default_factory=Metadata)
    elements: list[Element] = field(default_factory=list)
    package_configurations: PackageConfigurations = field(default_factory=dict)
