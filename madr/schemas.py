from pydantic import BaseModel, ConfigDict


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(RomancistaSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RomancistaList(BaseModel):
    romancistas: list[RomancistaPublic]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class Message(BaseModel):
    message: str
