from fastapi import Depends, Form
from app.utils.ontology import get_instruments
from app.api.schemas.instrument_schemas import InstrumentsResponse, Artist

def get(artists: str):
    instruments = get_instruments(artists)
    for instrument in instruments:
        print(instrument)
    
    return InstrumentsResponse(instruments=instruments)