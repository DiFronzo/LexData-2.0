import json
import logging
from typing import Dict, List, Optional

from .claim import Claim
from .entity import Entity
from .form import Form
from .language import Language
from .sense import Sense
from .wikidatasession import WikidataSession


class Lexeme(Entity):
    """Wrapper around a dict to represent a Lexeme"""

    def __init__(self, repo: WikidataSession, id_lex: str):
        super().__init__(repo)
        self.get_lex(id_lex)

    def get_lex(self, id_lex: str):
        """This function gets and returns the data of a lexeme for a given id.

        :param id_lex: Lexeme identifier (example: "L2")
        :type  id_lex: str
        :returns: Simplified object representation of Lexeme

        """

        PARAMS = {"action": "wbgetentities", "format": "json", "ids": id_lex}

        DATA = self.repo.get(PARAMS)

        self.update(DATA["entities"][id_lex])

    @property
    def lemma(self) -> str:
        """
        The lemma of the lexeme as string

        :rtype: str
        """
        return list(self["lemmas"].values())[0]["value"]

    @property
    def language(self) -> str:
        """
        The language code of the lexeme as string

        :rtype: str
        """
        return list(self["lemmas"].values())[0]["language"]

    @property
    def forms(self) -> List[Form]:
        """
        List of all forms

        :rtype: List[Form]
        """
        return [Form(self.repo, f) for f in super().get("forms", [])]

    @property
    def senses(self) -> List[Sense]:
        """
        List of all senses

        :rtype: List[Sense]
        """
        return [Sense(self.repo, s) for s in super().get("senses", [])]

    def create_sense(
        self, glosses: Dict[str, str], claims: Optional[List[Claim]] = None
    ) -> str:
        """Create a sense for the lexeme.

        :param glosses: glosses for the sense
        :type  glosses: Dict[str, str]
        :param claims: claims to add to the new form
        :rtype: str
        """
        # Create the json with the sense's data
        data_sense: Dict[str, Dict[str, Dict[str, str]]] = {"glosses": {}}
        for lang, gloss in glosses.items():
            data_sense["glosses"][lang] = {"value": gloss, "language": lang}

        # send a post to add sense to lexeme
        PARAMS = {
            "action": "wbladdsense",
            "format": "json",
            "lexemeId": self.id,
            "token": "__AUTO__",
            "bot": "1",
            "data": json.dumps(data_sense),
        }
        DATA = self.repo.post(PARAMS)
        added_sense = Sense(self.repo, DATA["sense"])
        id_sense = DATA["sense"]["id"]
        logging.info("Created sense: %s", id_sense)

        # Add the claims
        if claims:
            added_sense.add_claims(claims)

        # Add the created form to the local lexeme
        self["senses"].append(added_sense)

        return id_sense

    def create_form(
        self,
        form: str,
        infos_gram: List[str],
        language: Optional[Language] = None,
        claims: Optional[List[Claim]] = None,
    ) -> str:
        """Create a form for the lexeme.

        :param form: the new form to add
        :type  form: str
        :param infos_gram: grammatical features
        :type  infos_gram: List[str]
        :param language: the language of the form
        :type  language: Optional[Language]
        :param claims: claims to add to the new form
        :returns: The id of the form
        :rtype: str

        """

        if language is None:
            languagename = self.language
        else:
            languagename = language.short

        # Create the json with the forms's data
        data_form = json.dumps(
            {
                "representations": {
                    languagename: {"value": form, "language": languagename}
                },
                "grammaticalFeatures": infos_gram,
            }
        )

        # send a post to add form to lexeme
        PARAMS = {
            "action": "wbladdform",
            "format": "json",
            "lexemeId": self.id,
            "token": "__AUTO__",
            "bot": "1",
            "data": data_form,
        }
        DATA = self.repo.post(PARAMS)
        added_form = Form(self.repo, DATA["form"])
        id_form = DATA["form"]["id"]
        logging.info("Created form: %s", id_form)

        # Add the claims
        if claims:
            added_form.add_claims(claims)

        # Add the created form to the local lexeme
        self["forms"].append(added_form)

        return id_form

    def create_claims(self, claims: Dict[str, List[str]]):
        """Add claims to the Lexeme.

        create_claim() is deprecated and might be removed in future versions.
        Use Entity.add_claims() instead.

        :param claims: The set of claims to be added

        """
        logging.warning(
            "create_claim() is deprecated and might be removed in future versions."
            + " Use Entity.add_claims() instead"
        )
        self.__create_claims__(claims)

    def __repr__(self) -> str:
        return "<Lexeme '{}'>".format(self.id)

    def update_from_json(self, data: str, overwrite=False):
        """Update the lexeme from a json-string.

        This is a lower level function usable to save arbitrary modifications
        on a lexeme. The data has to be supplied in the right format by the
        user.

        :param data: Data update: See the API documentation about the format.
        :param overwrite: If set the whole entity is replaced by the supplied data
        """
        PARAMS: Dict[str, str] = {
            "action": "wbeditentity",
            "format": "json",
            "bot": "1",
            "id": self.id,
            "token": "__AUTO__",
            "data": data,
        }
        if overwrite:
            PARAMS["clear"] = "true"
        DATA = self.repo.post(PARAMS)
        if DATA.get("success") != 200:
            raise ValueError(DATA)
        logging.info("Updated from json data")
        # Due to limitations of the API, the returned data cannot be used to
        # update the instance. Therefore, reload the lexeme.
        self.get_lex(self.id)
