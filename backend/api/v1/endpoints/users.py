from typing import List
from fastapi import (APIRouter,
                     Depends)

from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.db.models import User
from backend.schemas.user import (UserResponse,
                                  UserUpdate)
from backend.crud.user import (read,
                               update,
                               delete)

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/users', response_model=List[UserResponse])
async def get_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await read(db, current_user, user_list=True)

@router.get('/profile', response_model=UserResponse)
async def profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await read(db, current_user)

@router.patch('/update/{user_id:int}')
async def update_user(
        data: UserUpdate, user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await update(user_id, current_user, db, data )


@router.delete('/delete/{user_id:int}')
async def delete_user(
        user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete(user_id, current_user, db)
