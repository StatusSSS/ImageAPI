from pydantic import BaseModel



class GetTokenModel(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str