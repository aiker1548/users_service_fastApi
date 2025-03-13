import bcrypt

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import Integer, String, LargeBinary

from src.auth import create_access_token
from src.users.utils import hash_password

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)
    

    @property
    def token(self) -> dict:
        # Например, включаем username и id в токен
        token = create_access_token({"sub": self.username, "user_id": self.id}, expires_delta=None)
        return {"access_token": token, "token_type": "bearer"}
    

    def set_password(self, password: str) -> None:
        """Set a new password"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)
