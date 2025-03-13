from pydantic import BaseModel

class CorpusBase(BaseModel):
    name: str
    text: str

class CorpusCreate(CorpusBase):
    """
    То, что передаём при загрузке корпуса.
    """
    pass

class CorpusRead(BaseModel):
    """
    То, что возвращаем, когда запрашиваем список корпусов.
    """
    id: int
    name: str

    class Config:
        orm_mode = True
