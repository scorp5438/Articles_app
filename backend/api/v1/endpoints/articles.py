from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.article import (ArticleResponse,
                                     ArticleCreate,
                                     ArticleUpdate)
from backend.crud.articles import (create,
                                   read,
                                   update,
                                   delete)

router = APIRouter(prefix='/articles', tags=['articles'])


@router.post('/create')
async def create_article(
        article: ArticleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id

    return await create(current_user_id, article, db)


@router.get('/', response_model=List[ArticleResponse])
async def show_article(db: Session = Depends(get_db)):
    return await read(db)


@router.patch('/update/{article_id:int}')
async def update_article(
        data: ArticleUpdate,
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    return await update(data, article_id, current_user_id, db)


@router.delete('/delete/{article_id:int}')
async def delete_article(
        article_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    return await delete(article_id, current_user_id, db)
