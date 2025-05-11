import logging
from functools import wraps
from typing import Callable, Optional, Type

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import (status,
                     HTTPException)

from backend.db.models import User
from backend.db.session import Base
from backend.schemas.article import ArticleUpdate
from backend.schemas.user import UserUpdate

logger_console = logging.getLogger('console_logger')
logger_file = logging.getLogger('file_logger')


def check_user_permissions(model: Type[Base]) -> Callable:
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
                logger_file.warning(f'{model.__name__} not found')
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'{model.__name__} not found'
                )

            if instance.author_id != current_user.id and not current_user.is_staff:
                logger_file.warning('You don`t have permission')
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You don`t have permission'
                )

            if data:
                return await func(instance_id, current_user, db, data, *args, **kwargs)
            return await func(instance_id, current_user, db, *args, **kwargs)

        return wrapper

    return decorator


def check_is_activate_permissions(schema: Type[BaseModel]) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(
                current_user: User,
                obj: schema,
                db: Session,
                *args,
                **kwargs,
        ):
            if not current_user.is_active:
                logger_file.warning('You need to confirm email')
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You need to confirm email'
                )
            return await func(current_user, obj, db, *args, **kwargs)

        return wrapper

    return decorator


def check_is_staff_or_self_permissions(func) -> Callable:
    @wraps(func)
    async def wrapper(
            user_id: int,
            current_user: User,
            db: Session,
            data: Optional[UserUpdate] = None,
            *args,
            **kwargs,
    ):
        if current_user.id != user_id and not current_user.is_staff:
            logger_file.warning('You don`t have permission')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You don`t have permission'
            )
        if data:
            return await func(user_id, current_user, db, data, *args, **kwargs)
        return await func(user_id, current_user, db, *args, **kwargs)

    return wrapper
