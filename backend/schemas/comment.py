from pydantic import (BaseModel,
                      Field)
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    article_id: int = Field()


class CommentResponse(BaseModel):
    id: int
    content: str
    article_id: int
    author_name: str
    created_at: datetime
