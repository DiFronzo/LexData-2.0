#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import os

import pytest

import LexData


@pytest.fixture
def credentials():
    try:
        username = os.environ['LEXDATA_USERNAME']
        password = os.environ['LEXDATA_PASSWORD']
        return username, password
    except KeyError:
        with open(Path.home() / ".wikipass") as f:
            username, password, *_ = f.read().split("\n")
        return username, password


@pytest.fixture
def repo(credentials):
    username, password = credentials
    return LexData.WikidataSession(username, password)


@pytest.fixture
def repoTestWikidata():
    test = LexData.WikidataSession()
    test.URL = "https://test.wikidata.org/w/api.php"
    test.CSRF_TOKEN = "+\\"
    return test


@pytest.fixture
def repoWikidata():
    test = LexData.WikidataSession()
    test.URL = "https://wikidata.org/w/api.php"
    test.CSRF_TOKEN = "+\\"
    return test


def test_auth(credentials):
    with pytest.raises(Exception):
        assert LexData.WikidataSession("Username", "Password")
    anon = LexData.WikidataSession()
    LexData.Lexeme(anon, "L2")
    # anon.maxlag = 1
    # LexData.Lexeme(anon, "L2")


def test_lexeme(repo):
    L2 = LexData.Lexeme(repo, "L2")

    assert L2.lemma == "first"
    assert L2.language == "en"
    claims = L2.claims
    assert isinstance(claims, dict)

    examples = claims.get("P5831", [])
    assert len(examples) >= 1
    example = examples[0]
    assert isinstance(repr(example), str)
    assert example.property == "P5831"
    assert example.rank == "normal"
    assert example.numeric_rank == 0
    assert example.type == "monolingualtext"
    assert example.pure_value == "He was first in line."
    assert example.value["text"] == "He was first in line."
    assert example.value["language"] == "en"


def test_sense(repo):
    L2 = LexData.Lexeme(repo, "L2")
    assert str(L2)
    assert repr(L2)

    senses = L2.senses
    assert isinstance(senses, list)
    for sense in senses:
        assert isinstance(repr(sense), str)
        assert isinstance(sense.glosse(), str)
        assert isinstance(sense.glosse("de"), str)
        assert sense.glosse("en") == sense.glosse()
        assert sense.glosse("XX") == sense.glosse()
        del sense["glosses"]["en"]
        assert isinstance(sense.glosse("XX"), str)
        assert isinstance(sense.claims, dict)


def test_form(repo):
    L2 = LexData.Lexeme(repo, "L2")
    forms = L2.forms
    assert isinstance(forms, list)
    for form in forms:
        assert isinstance(repr(form), str)
        assert isinstance(form.form, str)
        assert isinstance(form.claims, dict)


def test_writes(repoTestWikidata):
    L123 = LexData.Lexeme(repoTestWikidata, "L123")

    L123.create_claims({"P7": ["Q100"]})
    L123.add_claims({"P7": ["Q100"]})

    L123.create_form("test", ["Q100"])

    L123.create_sense({"de": "testtest", "en": "testtest"})
    L123.create_sense({"de": "more tests", "en": "more tests"}, claims={})
    L123.create_sense({"en": "even more tests"}, claims={"P7": ["Q100"]})


def test_search(repo):
    results = LexData.search_lexemes(repo, "water", LexData.language.lang_en, "Q1084")
    assert len(results) == 1
    assert results[0].get("id") == "L3302"

    result = LexData.get_or_create_lexeme(repo, "water", LexData.language.lang_en, "Q1084")
    assert result["id"] == "L3302"


def test_detatchedClaim(repo):
    LexData.Claim(property_id="P369", value="Q1")
    LexData.Claim(property_id="P856", value="http://example.com/")
    LexData.Claim(property_id="P2534", value="\frac{1}{2}")
    quantity = LexData.Claim(property_id="P2021", value=6)
    assert quantity.pure_value == 6
    date = LexData.Claim(property_id="P580", value=datetime.now())
    assert type(date.pure_value) is str
    with pytest.raises(TypeError):
        LexData.Claim(property_id="P856", value=1)
        LexData.Claim(property_id="P2021", value="foo")
        LexData.Claim(property_id="P580", value=1)
        LexData.Claim(property_id="P580", value="foo")
    with pytest.raises(Exception):
        LexData.Claim(property_id="P0", value="foo")


def test_createLexeme(repoTestWikidata):
    LexData.create_lexeme(repoTestWikidata, "foobar", LexData.language.lang_en, "Q100")
