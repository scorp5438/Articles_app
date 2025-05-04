import logging
from typing import Optional

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.decorators import (check_user_permissions,
                                     check_is_activate_permissions)
from backend.crud.user import get_user
from backend.db.models import Article, User
from backend.schemas.article import (ArticleCreate,
                                     ArticleUpdate,
                                     ArticleResponse)

logger_console = logging.getLogger('console_logger')
logger_file = logging.getLogger('file_logger')


async def get_article(db: Session, article_id: Optional[int] = None):
    if article_id is None:
        result = await db.execute(select(Article).order_by(Article.id))
        return result.scalars().all()

    result = await db.execute(select(Article).filter(Article.id == article_id))
    article = result.scalars().first()

    return article


@check_is_activate_permissions(schema=ArticleCreate)
async def create(
        current_user: User,
        article: ArticleCreate,
        db: Session
):
    article_db = Article(
        title=article.title,
        content=article.content,
        author_id=current_user.id,
    )

    db.add(article_db)
    await db.commit()
    await db.refresh(article_db)
    logger_console.info('Article created')

    return {'message': 'Article created', 'status': status.HTTP_201_CREATED}


async def read(db: Session):
    result = await db.execute(select(Article).order_by(Article.id))
    articles = result.scalars().all()

    article_response = []
    for article in articles:
        if article.author_id is not None:
            user = await get_user(db, user_id=article.author_id)
            author_name = user.full_name
        else:
            author_name = 'Удаленный пользователь'
        article_response.append(
            ArticleResponse(
                id=article.id,
                title=article.title,
                content=article.content,
                author_name=author_name,
                created_at=article.created_at,
                updated_at=article.updated_at,
            ))

    return article_response


@check_user_permissions(Article)
async def update(
        article_id: int,
        current_user: User,
        db: Session,
        data: ArticleUpdate
):
    article = await get_article(db, article_id)

    update_data: dict = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)

    db.add(article)
    await db.commit()
    await  db.refresh(article)
    logger_console.info('Article updated')

    return {'message': 'Article updated', 'status': status.HTTP_200_OK}


@check_user_permissions(Article)
async def delete(
        article_id: int,
        current_user: User,
        db: AsyncSession
):
    article = await get_article(db, article_id)

    await db.delete(article)
    await db.commit()
    logger_console.info('Article deleted')

    return {'message': 'Article deleted', 'status': status.HTTP_200_OK}
