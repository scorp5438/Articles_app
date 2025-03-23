from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=10)


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
