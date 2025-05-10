import logging

from sqlalchemy.orm import Session
from fastapi import status

from sqlalchemy.future import select
from backend.core.decorators import (check_user_permissions,
                                     check_is_activate_permissions)
from backend.crud.user import get_user
from backend.db.models import User
from backend.schemas.comment import (CommentCreate,
                                     CommentResponse)
from backend.db.models.comment import Comment
from crud.articles import get_article

logger_console = logging.getLogger('console_logger')
logger_file = logging.getLogger('file_logger')


@check_is_activate_permissions(schema=CommentCreate)
async def create(
        current_user: User,
        comment: CommentCreate,
        db: Session
):
    await get_article(db, comment.article_id)
    comment_db = Comment(
        content=comment.content,
        article_id=comment.article_id,
        author_id=current_user.id
    )

    db.add(comment_db)
    await db.commit()
    await db.refresh(comment_db)
    logger_console.info('Comment successfully added')

    return {'message': 'Comment successfully added', 'status': status.HTTP_201_CREATED}


async def read(article_id: int, db: Session):
    result = await db.execute(select(Comment).filter(Comment.article_id == article_id).order_by(Comment.id))
    comments = result.scalars().all()
    comments_response = []
    for comment in comments:
        if comment.author_id is not None:
            user = await get_user(db=db, user_id=comment.author_id)
            author_name = user.full_name
        else:
            author_name = 'Удаленный пользователь'
        comments_response.append(
            CommentResponse(
                id=comment.id,
                content=comment.content,
                article_id=comment.article_id,
                author_name=author_name,
                created_at=comment.created_at,
            ))
    return comments_response


@check_user_permissions(Comment)
async def delete(comment_id: int, current_user: User, db: Session):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()

    await db.delete(comment)
    await db.commit()
    logger_console.info('Comment deleted')

    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}
