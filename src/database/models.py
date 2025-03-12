import bcrypt
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
import jwt

from src.auth import create_access_token
from src.auth import hash_password
from config import config

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)

    def check_password(self, password: str) -> bool:
        return self.password_hash == password

    def create_access_token(self) -> dict:
        # Например, включаем username и id в токен
        token = create_access_token({"sub": self.username, "user_id": self.id}, expires_delta=None)
        return {"access_token": token, "token_type": "bearer"}
    
    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches stored hash"""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    @property
    def token(self):
        now = datetime.utcnow()
        exp = (now + timedelta(seconds=config.DISPATCH_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, config.DISPATCH_JWT_SECRET, algorithm=config.DISPATCH_JWT_ALG)