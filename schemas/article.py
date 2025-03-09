from pydantic import BaseModel, Field
from datetime import datetime


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=10)

class ArticleResponse(BaseModel):
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
