from typing import Any, Dict, Optional, Tuple, Union

from .utils import build_snak


class Claim(dict):
    """Wrapper around a dict to represent a Claim

    There are two types of Claim objects:

    * Claims that where received from an existing entity.
    * Claims that where created by the user by Claim(property_id, value) and
      have not yet been uploaded to Wikidata. These are called 'Detached Claims',
      since they don't belong to any entity.  They don't have an id nor an hash.
      They can be added to an entity by the function Entity.add_claims().

    Currently modifications on both types of claims can't be uploaded, except
    by use of the low level API call Lexeme.update_from_json().
    """

    # Hack needed to define a property called property
    property_decorator = property

    def __init__(
        self,
        claim: Optional[Dict[str, Any]] = None,
        property_id: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        super().__init__()
        if isinstance(claim, dict) and not property_id and not value:
            self.update(claim)
        elif claim is None and property_id and value:
            self["mainsnak"] = build_snak(property_id, value)
            self["rank"] = "normal"
        else:
            raise TypeError(
                "Claim() received an invalid combination of arguments expected one of:"
                + " * (dict claimObject)"
                + " * (str property_id, value)"
            )

    @property_decorator
    def value(self) -> Dict[str, Any]:
        """
        Return the value of the claim. The type depends on the data type.
        """
        return self["mainsnak"]["datavalue"]["value"]

    @property_decorator
    def type(self) -> str:
        """
        Return the data type of the claim.

        :rtype: str
        """
        return self["mainsnak"]["datatype"]

    @property_decorator
    def property(self) -> str:
        """
        Return the id of the property of the claim.

        :rtype: str
        """
        return self["mainsnak"]["property"]

    @property_decorator
    def rank(self) -> str:
        """
        Return the rank of the claim.

        :rtype: str
        """
        return self["rank"]

    @property_decorator
    def numeric_rank(self) -> int:
        """
        Return the rank of the claim as integer.

        :rtype: int
        """
        if self.rank == "normal":
            return 0
        elif self.rank == "preferred":
            return 1
        elif self.rank == "deprecated":
            return -1
        raise NotImplementedError("Unknown or invalid rank {}".format(self.rank))

    @property_decorator
    def pure_value(self) -> Union[str, int, float, Tuple[float, float]]:
        """
        Return just the 'pure' value, what this is depends on the type of the value:

        * wikibase-entity: the id as string, including 'L/Q/P'-prefix
        * string: the string
        * monolingualtext: the text as string
        * quantity: the amount as float
        * time: the timestamp as string in format ISO 8601
        * globecoordinate: tuple of latitude and longitude as floats

        Be aware that for most types this is not the full information stored in
        the value.
        """
        value = self.value
        vtype = self.type
        if vtype == "wikibase-entityid":
            return value["id"]
        if vtype == "string":
            return value
        if vtype == "monolingualtext":
            return value["text"]
        if vtype == "quantity":
            return float(value["amount"])
        if vtype == "time":
            return value["time"]
        if vtype == "globecoordinate":
            return float(value["latitude"]), float(value["longitude"])
        raise NotImplementedError

    def __repr__(self) -> str:
        if "id" in self:
            return "<Claim '{}'>".format(repr(self.value))
        else:
            return "<Detached Claim '{}'>".format(repr(self.value))
