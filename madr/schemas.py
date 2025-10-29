from pydantic import BaseModel, ConfigDict, EmailStr


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(RomancistaSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RomancistaList(BaseModel):
    romancistas: list[RomancistaPublic]


class RomancistaUpdate(BaseModel):
    nome: str | None = None


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 20


class FilterRomancista(FilterPage):
    nome: str | None = None


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    senha: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserDB(UserSchema):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str
