from sqlalchemy import (Column,
                        Integer,
                        String,
                        Boolean,
                        Date,
                        DateTime,
                        func)
from sqlalchemy.orm import relationship

from ..session import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, index=True)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(Date, server_default=func.now(), index=True)
    avatar_url = Column(String, nullable=True, index=True)
    is_staff = Column(Boolean, default=False, index=True)
    conf_reg_link = Column(String, nullable=True, unique=True, index=True)

    # Отношение "один ко многим" с моделью Article
    articles = relationship('Article', back_populates='author')

    # Отношение "один ко многим" с моделью Comment
    comments = relationship('Comment', back_populates='commentator')

    def __str__(self):
        return f'id: {self.id} email: {self.email} full_name: {self.full_name}'


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expire_at = Column(DateTime)
