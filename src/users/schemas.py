from pydantic import BaseModel, EmailStr

# Модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str

# Модель для представления пользователя в ответах
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True