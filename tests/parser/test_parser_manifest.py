from loclass_ldl.model import Metadata
from loclass_ldl.parser import parse_document


def test_parse_extended_metadata():
    source = """---
title: Technische Dokumentation
subtitle: Systemübersicht
author: Frank Sieger
company: ACME GmbH
customer: Beispielkunde
language: de
theme: loclass
version: 0.2.0
revision: 1
date: 2026-07-07
---
"""

    document = parse_document(source)

    assert document.metadata == Metadata(
        title="Technische Dokumentation",
        subtitle="Systemübersicht",
        author="Frank Sieger",
        company="ACME GmbH",
        customer="Beispielkunde",
        language="de",
        theme="loclass",
        version="0.2.0",
        revision="1",
        date="2026-07-07",
    )
