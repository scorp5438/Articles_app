from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..session import Base


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now(), index=True)

    # Связь с моделью User
    author = relationship('User', back_populates='articles')

    # Связь с моделью Comment (один ко многим)
    comment = relationship('Comment', back_populates='article')
