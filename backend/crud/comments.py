from sqlalchemy.orm import Session
from fastapi import (status,
                     HTTPException)
from sqlalchemy.future import select

from backend.core.decorators import check_article_permissions
from backend.crud.user import get_user
from backend.db.models import User
from backend.schemas.comment import (CommentCreate,
                                     CommentResponse)
from backend.db.models.comment import Comment


async def create(
        comment: CommentCreate,
        current_user: User,
        db: Session
):
    comment_db = Comment(
        content=comment.content,
        article_id=comment.article_id,
        author_id=current_user.id
    )

    db.add(comment_db)
    await db.commit()
    await db.refresh(comment_db)
    return {'message': 'Comment successfully added', 'status': status.HTTP_201_CREATED}


async def read(article_id: int, db: Session):
    result = await db.execute(select(Comment).filter(Comment.article_id == article_id).order_by(Comment.id))
    comments = result.scalars().all()

    comments_response = [
        CommentResponse(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            author_name=(await get_user(db=db, user_id=comment.author_id)).full_name,
            created_at=comment.created_at,
        )
        for comment in comments
    ]
    return comments_response


@check_article_permissions(Comment)
async def delete(comment_id: int, current_user: User, db: Session):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()

    await db.delete(comment)
    await db.commit()
    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}
