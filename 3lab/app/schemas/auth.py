from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserShow(BaseModel):
    id: int
    email: str
    class Config:
        orm_mode = True
