from pydantic import BaseModel

class Artist(BaseModel):
    name: str

class InstrumentResponse(BaseModel):
    name: str

class InstrumentsResponse(BaseModel):
    instruments: list[InstrumentResponse]