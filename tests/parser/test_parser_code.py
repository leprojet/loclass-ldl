from loclass_ldl.parser import parse_code


def test_parse_code():
    source = """
code
  params
    label: lst:hello
    caption: Hello World
    language: python

  body
    ---
    def hello():
        print("Hello World")
    ---
"""

    code = parse_code(source)

    assert code.body == [
        "def hello():",
        '    print("Hello World")',
    ]


def test_code_preserves_blank_lines():
    source = """
code
  params
    language: python

  body
    ---
    def hello():

        print("Hello")
    ---
"""

    code = parse_code(source)

    assert code.body == [
        "def hello():",
        "",
        '    print("Hello")',
    ]
