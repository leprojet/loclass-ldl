import pytest

from loclass_ldl.parser import parse_image


def test_parse_image():
    source = """
image
  params
    label: fig:logo
    caption: Firmenlogo

  file
    logo.png
"""

    image = parse_image(source)

    assert image.label == "fig:logo"
    assert image.caption == "Firmenlogo"
    assert image.file == "logo.png"


def test_image_requires_file():
    source = """
image
  params
    caption: Firmenlogo
"""

    with pytest.raises(ValueError):
        parse_image(source)
