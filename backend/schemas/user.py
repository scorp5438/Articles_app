import re
from typing import Optional
from datetime import date

from pydantic import (BaseModel,
                      EmailStr,
                      Field,
                      field_validator,
                      ConfigDict)

from backend.core.config import PATTERN_LITE


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

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: date
    is_staff: Optional[bool]
    avatar_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


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
