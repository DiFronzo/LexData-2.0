import functools
import json
from datetime import datetime
from typing import Any, Dict

from .wikidatasession import WikidataSession


@functools.lru_cache()
def get_property_type(property_id: str):
    repo = WikidataSession()
    query = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": "Property:" + property_id,
        "rvprop": "content",
    }
    DATA = repo.get(query)
    json_str = list(DATA["query"]["pages"].values())[0]["revisions"][0]["*"]
    content = json.loads(json_str)
    return content["datatype"]


def build_data_value(datatype: str, value):
    if datatype in [
        "wikibase-lexeme",
        "wikibase-form",
        "wikibase-sense",
        "wikibase-item",
        "wikibase-property",
    ]:
        if type(value) == dict:
            return {"value": value, "type": "wikibase-entity"}
        elif type(value) == str:
            value = {"entity-type": datatype[9:], "id": value}
            return {"value": value, "type": "wikibase-entity"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype in [
        "string",
        "tabular-data",
        "geo-shape",
        "url",
        "musical-notation",
        "math",
        "commonsMedia",
    ]:
        if type(value) == dict:
            return {"value": value, "type": "string"}
        elif type(value) == str:
            return {"value": {"value": value}, "type": "string"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "monolingualtext":
        if type(value) == dict:
            return {"value": value, "type": "monolingualtext"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "globe-coordinate":
        if type(value) == dict:
            return {"value": value, "type": "globecoordinate"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "quantity":
        if type(value) == dict:
            return {"value": value, "type": "quantity"}
        if type(value) in [int, float]:
            value_obj = {
                "amount": "%+f" % value,
                "unit": "1",
            }
            return {"value": value_obj, "type": "time"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "time":
        if type(value) == dict:
            return {"value": value, "type": "time"}
        if type(value) == datetime:
            cleaned_date_time = value.replace(hour=0, minute=0, second=0, microsecond=0)
            value_obj: Dict[str, Any] = {
                "time": "+" + cleaned_date_time.isoformat() + "Z",
                "timezone": 0,
                "before": 0,
                "after": 0,
                "precision": 11,
                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
            }
            return {"value": value_obj, "type": "time"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    else:
        raise NotImplementedError(f"Datatype {datatype} not implemented")


def build_snak(property_id: str, value):
    data_type = get_property_type(property_id)
    data_value = build_data_value(data_type, value)

    return {
        "snaktype": "value",
        "property": property_id,
        "datavalue": data_value,
        "datatype": data_type,
    }
