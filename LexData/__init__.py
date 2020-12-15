# -*-coding:utf-8-*
import json
import logging
from typing import List

from .claim import Claim
from .form import Form
from .sense import Sense
from .language import Language
from .lexeme import Lexeme
from .wikidatasession import WikidataSession


def get_or_create_lexeme(
    repo: WikidataSession, lemma: str, lang: Language, catLex: str
) -> Lexeme:
    """Search for a lexeme in wikidata if not found, create it

    :param repo: Wikidata Session
    :type  repo: WikidataSession
    :param lemma: the lemma of the lexeme
    :type  lemma: str
    :param lang: language of the lexeme
    :type  lang: Language
    :param catLex: lexical Category of the lexeme
    :type  catLex: str
    :returns: Lexeme with the specified properties (created or found)
    :rtype: Lexeme

    """
    lexemes = search_lexemes(repo, lemma, lang, catLex)
    if len(lexemes) == 1:
        return lexemes[0]
    elif len(lexemes) > 1:
        logging.warning("Multiple lexemes found, using first one.")
        return lexemes[0]
    else:
        return create_lexeme(repo, lemma, lang, catLex)


def search_lexemes(
    repo: WikidataSession, lemma: str, lang: Language, catLex: str
) -> List[Lexeme]:
    """
    Search for a lexeme by it's label, language and lexical category.

    :param repo: Wikidata Session
    :type  repo: WikidataSession
    :param lemma: the lemma of the lexeme
    :type  lemma: str
    :param lang: language of the lexeme
    :type  lang: Language
    :param catLex: lexical Category of the lexeme
    :type  catLex: str
    :returns: List of Lexemes with the specified properties
    :rtype: List[Lexeme]
    """
    # the language we specify in search is currently not used by the search
    # set it nevertheless, except if it is a Language without ISO code
    if lang.short[:3] == "mis":
        searchlang = "en"
    else:
        searchlang = lang.short

    PARAMS = {
        "action": "wbsearchentities",
        "language": searchlang,
        "type": "lexeme",
        "search": lemma,
        "format": "json",
        "limit": "10",
    }

    DATA = repo.get(PARAMS)

    if "error" in DATA:
        raise Exception(DATA["error"])

    # Iterate over all results and check for matches. Do not rely on
    # match-results, since they can differ for smaller languages – use them
    # however to avoid unnecessary queries.
    lexemes = []
    for item in DATA["search"]:
        if item["label"] == lemma:
            if "language" in item["match"]:
                if item["match"]["language"] != lang.short and item["match"] != "und":
                    continue
            idLex = item["id"]
            lexeme = Lexeme(repo, idLex)
            if lexeme["language"] == lang.qid and lexeme["lexicalCategory"] == catLex:
                logging.info("Found lexeme: %s", idLex)
                lexemes.append(lexeme)
    return lexemes


def create_lexeme(
    repo: WikidataSession, lemma: str, lang: Language, catLex: str, claims=None
) -> Lexeme:
    """Creates a lexeme

    :param repo: Wikidata Session
    :type  repo: WikidataSession
    :param lemma: value of the lexeme
    :type  lemma: str
    :param lang: language
    :type  lang: Language
    :param catLex: lexicographical category
    :param claims: claims to add to the lexeme (Default value = None) -> Lexem)
    :type  catLex: str
    :returns: The created Lexeme
    :rtype: Lexeme

    """

    # Create the json with the lexeme's data
    data_lex = json.dumps(
        {
            "type": "lexeme",
            "lemmas": {lang.short: {"value": lemma, "language": lang.short}},
            "language": lang.qid,
            "lexicalCategory": catLex,
            "forms": [],
        }
    )

    # Send a post to edit a lexeme
    PARAMS = {
        "action": "wbeditentity",
        "format": "json",
        "bot": "1",
        "new": "lexeme",
        "token": "__AUTO__",
        "data": data_lex,
    }

    DATA = repo.post(PARAMS)
    # Get the id of the new lexeme
    idLex = DATA["entity"]["id"]

    logging.info("Created lexeme: %s", idLex)
    lexeme = Lexeme(repo, idLex)

    if claims:
        lexeme.createClaims(claims)

    return lexeme
