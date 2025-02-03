from pydantic import BaseModel, ConfigDict


class Skill(BaseModel):
    instrument: str
    level: float

class ArtistSkillsRequest(BaseModel):
    artists: list[str]
    skills: list[Skill] | None = None


class InstrumentResponse(BaseModel):
    name: str
    weight: float

    model_config = ConfigDict(from_attributes=True)

class InstrumentsResponse(BaseModel):
    instruments: list[InstrumentResponse]
