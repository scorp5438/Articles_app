from typing import List

from sqlalchemy.orm import Session
from fastapi import (APIRouter,
                     Depends)

from core.security import get_current_user
from db.models import User
from db.session import get_db
from schemas.comment import (CommentCreate,
                             CommentResponse)
from crud.comments import (create,
                           read,
                           delete)

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/create')
async def create_comment(
        comment: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    return await create(comment, current_user_id, db)


@router.get('/{article_id:int}', response_model=List[CommentResponse])
async def show_comment(article_id: int, db: Session = Depends(get_db)):
    return await read(article_id, db)


# @router.patch('/')
# async def update_comment():
#     ...
#

@router.delete('/delete/{comment_id:int}')
async def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    return await delete(comment_id, db, current_user_id)
