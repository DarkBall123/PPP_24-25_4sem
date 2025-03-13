from pydantic import BaseModel, EmailStr

# базовая схема, которая содержит только email
class UserBase(BaseModel):
    email: EmailStr

# схема для создания пользователя (передаём пароль)
class UserCreate(UserBase):
    password: str

# схема для чтения пользователя [то, что отдадим наружу ;)]
class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True
