from sqlalchemy.orm import Session
from fastapi import status, HTTPException
from sqlalchemy.future import select

from crud.user import get_user
from db.models import User
from schemas.comment import CommentCreate, CommentResponse
from db.models.comment import Comment


async def create(
        comment: CommentCreate,
        current_user_id: id,
        db: Session
):
    comment_db = Comment(
        content=comment.content,
        article_id=comment.article_id,
        author_id=current_user_id
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
            content=comment.content,
            article_id=comment.article_id,
            author_name=(await get_user(db=db, user_id=comment.author_id)).full_name,
            created_at=comment.created_at,
        )
        for comment in comments
    ]
    return comments_response


async def delete(comment_id: int, db: Session, current_user_id: User):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found'
        )

    if current_user_id != comment.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don`t have permission'
        )

    await db.delete(comment)
    await db.commit()
    return {'message': 'Comment deleted', 'status': status.HTTP_200_OK}