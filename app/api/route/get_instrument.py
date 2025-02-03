from fastapi import Depends, Form
from app.utils.ontology import get_instruments
from app.api.schemas.instrument_schemas import InstrumentsResponse

def get(artists: str = None, ):
    artists = [artist.strip() for artist in artists.split(",")]
    instruments = get_instruments(artists)

    return InstrumentsResponse(instruments=instruments)