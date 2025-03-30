from typing import Optional

from sqlalchemy.orm import Session
from fastapi import (status,
                     HTTPException)
from sqlalchemy.future import select

from backend.core.decorators import check_article_permissions
from backend.crud.user import get_user
from backend.db.models import Article, User
from backend.schemas.article import (ArticleCreate,
                                     ArticleUpdate,
                                     ArticleResponse)


async def get_article(db: Session, article_id: Optional[int] = None):
    if article_id is None:
        result = await db.execute(select(Article).order_by(Article.id))
        return result.scalars().all()

    result = await db.execute(select(Article).filter(Article.id == article_id))
    article = result.scalars().first()

    return article


async def create(
        current_user_id: int,
        article: ArticleCreate,
        db: Session
):
    article_db = Article(
        title=article.title,
        content=article.content,
        author_id=current_user_id,
    )

    db.add(article_db)
    await db.commit()
    await db.refresh(article_db)
    return {'message': 'Article created', 'status': status.HTTP_201_CREATED}


async def read(db: Session):
    result = await db.execute(select(Article).order_by(Article.id))
    articles = result.scalars().all()
    article_response = [
        ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            author_name=(await get_user(db=db, user_id=article.author_id)).full_name,
            created_at=article.created_at,
            updated_at=article.updated_at,
        ) for article in articles
    ]
    return article_response


@check_article_permissions(Article)
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
    return {'message': 'Article updated', 'status': status.HTTP_200_OK}


@check_article_permissions(Article)
async def delete(
        article_id: int,
        current_user: User,
        db: Session
):
    article = await get_article(db, article_id)

    await db.delete(article)
    await db.commit()

    return {'message': 'Article deleted', 'status': status.HTTP_200_OK}
