import re
from typing import (Optional,
                    Self)
from datetime import date

from pydantic import (BaseModel,
                      EmailStr,
                      Field,
                      field_validator)

from backend.core.config import PATTERN_LITE
from backend.db.models.user import User


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=3, max_length=30)
    avatar_url: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_validator(cls, password: str) -> str:
        if re.match(PATTERN_LITE, password) is None:
            raise ValueError('Password must contain at least one digit')
        return password


class UserForEmail(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=30)

    @classmethod
    def from_orm(cls, user: User) -> Self:
        return cls(
            email=user.email,
            full_name=user.full_name
        )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: date
    is_staff: Optional[bool]
    avatar_url: Optional[str]


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None
    is_staff: Optional[bool] = None


# Схема для ответа с токеном
class Token(BaseModel):
    access_token: str
    token_type: str


# Схема для данных в токене
class TokenData(BaseModel):
    email: str | None = None
