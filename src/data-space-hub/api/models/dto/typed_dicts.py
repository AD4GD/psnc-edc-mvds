from typing import TypedDict, Dict, Any


class LocationDict(TypedDict):
    id : str
    country : str
    city : str
    postal_code : str
    street : str
    building_number : str
    created_at : int


class ParticipantDict(TypedDict):
    id : str
    did : str
    name : str
    full_name : str
    VAT_number : str
    protocol_url : str
    email : str
    location_id : str
    location : Dict[str, Any]
    created_at : int
