from pydantic import BaseModel, ConfigDict

class Artist(BaseModel):
    name: str

class InstrumentResponse(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class InstrumentsResponse(BaseModel):
    instruments: list[InstrumentResponse]