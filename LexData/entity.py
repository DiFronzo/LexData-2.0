import json
import logging
from typing import Dict, List, Union

from .claim import Claim
from .wikidatasession import WikidataSession


class Entity(dict):
    """
    Base class for all types of entities – currently: Lexeme, Form, Sense.
    Not yet implemented: Item, Property.
    """

    def __init__(self, repo: WikidataSession):
        super().__init__()
        self.repo = repo

    @property
    def claims(self) -> Dict[str, List[Claim]]:
        """
        All the claims of the Entity

        :rtype: Dict[str, List[Claim]]
        """
        if self.get("claims", {}):
            return {k: [Claim(c) for c in v] for k, v in self.get("claims", {}).items()}
        else:
            return {}

    def add_claims(self, claims: Union[List[Claim], Dict[str, List[str]]]):
        """
        Add claims to the entity.

        :param claims: The claims to be added to the entity.

                       There are two possibilities for this:

                       - A list of Objects of type Claim

                         Example: ``[Claim(property_id="P31", value="Q1")]``

                       - A dictionary with the property id as key and lists of
                         string formated entity ids as values.

                         Example: ``{"P31": ["Q1", "Q2"]}``

                       The first supports all datatypes, whereas the later
                       currently only supports datatypes of kind Entity.
        """
        if isinstance(claims, list):
            self.__set_claims__(claims)
        elif isinstance(claims, dict):
            self.__create_claims__(claims)
        else:
            raise TypeError("Invalid argument type:", type(claims))

    def __set_claims__(self, claims: List[Claim]):
        """
        Add prebuild claims to the entity

        :param claims: The list of claims to be added
        """
        for claim in claims:
            pid = claim.property
            self.__set_claim__(str(pid), claim)

    def __create_claims__(self, claims: Dict[str, List[str]]):
        """
        Create and add new claims to the entity.

        Only properties of some entity type are implemented:
        Item, Property, Lexeme, Form and Sense

        :param claims: The set of claims to be added
        """
        for cle, values in claims.items():
            for value in values:
                self.__set_entity_claim__(cle, value)

    def __set_entity_claim__(self, id_prop: str, id_str: str):
        """
        Add a claim of an entity-type to the entity.

        Supported types are Lexeme, Form, Sense, Item, Property.

        :param id_prop: id of the property (example: "P31")
        :param idItem: id of the entity (example: "Q1")
        """
        entity_id = int(id_str[1:])
        claim_value = json.dumps({"entity-type": "item", "numeric-id": entity_id})
        self.__set_claim__(id_prop, claim_value)

    def __set_claim__(self, id_prop: str, claim_value):
        PARAMS = {
            "action": "wbcreateclaim",
            "format": "json",
            "entity": self.id,
            "snaktype": "value",
            "bot": "1",
            "property": id_prop,
            "value": claim_value,
            "token": "__AUTO__",
        }

        DATA = self.repo.post(PARAMS)
        assert "claim" in DATA
        added_claim = DATA["claim"]
        logging.info("Claim added")

        # Add the created claim to the local entity instance
        if not self.get("claims", []):
            self["claims"] = {id_prop: added_claim}
        elif id_prop in self.claims:
            self.claims[id_prop].append(added_claim)
        else:
            self.claims[id_prop] = [added_claim]

    @property
    def id(self) -> str:
        entity_id = self.get("id")
        assert isinstance(entity_id, str)
        return entity_id

    def __str__(self) -> str:
        return super().__repr__()
