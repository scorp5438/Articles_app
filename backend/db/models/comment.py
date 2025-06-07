from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        ForeignKey,
                        func)
from sqlalchemy.orm import relationship

from ..session import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False, index=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), index=True)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Связь с моделью User
    commentator = relationship('User', back_populates='comments')

    # Связь с моделью Article (многие к одному)
    article = relationship('Article', back_populates='comments')
