import bcrypt
import secrets
import string

from pydantic import BaseModel, EmailStr, validator

from src.users.utils import hash_password

# Модель для создания пользователя
class User(BaseModel):
    username: str
    email: EmailStr
    password_hash: str

    @validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v
    


# Модель для представления пользователя в ответах
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserResponseWithToken(BaseModel):
    user: UserOut
    access_token: dict


class UserToken(BaseModel):
    username: str
    password: str