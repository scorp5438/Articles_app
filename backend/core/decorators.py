from functools import wraps
from typing import Callable, Optional, Type

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import (status,
                     HTTPException)

from backend.db.models import User, Article
from backend.db.session import Base
from backend.schemas.article import ArticleUpdate


def check_article_permissions(model: Type[Base]) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(
                instance_id: int,
                current_user: User,
                db: Session,
                data: Optional[ArticleUpdate] = None,
                *args,
                **kwargs,
        ):
            result = await db.execute(select(model).filter(model.id == instance_id))
            instance = result.scalars().first()

            if not instance:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'{model.__name__} not found'
                )

            if instance.author_id != current_user.id and not current_user.is_staff:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You don`t have permission'
                )
            if data:
                return await func(instance_id, current_user, db, data, *args, **kwargs)
            return await func(instance_id, current_user, db, *args, **kwargs)

        return wrapper

    return decorator
