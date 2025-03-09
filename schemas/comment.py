from pydantic import BaseModel, Field
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    article_id: int = Field()
    author_id: int = Field()


class CommentResponse(BaseModel):
    content: str
    article_id: int
    author_id: int
    created_at: datetime
