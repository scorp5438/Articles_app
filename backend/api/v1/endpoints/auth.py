from datetime import timedelta
from typing import List
from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.security import (verify_password,
                                   ACCESS_TOKEN_EXPIRE_MINUTES,
                                   create_access_token,
                                   get_current_user,
                                   oauth2_scheme)
from backend.db.session import get_db
from backend.db.models import User
from backend.schemas.user import (Token,
                                  UserCreate,
                                  UserResponse,
                                  UserUpdate)
from backend.crud.user import (create,
                               read,
                               update,
                               delete,
                               get_user, add_token, del_token)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = form_data.username
    db_user = await get_user(db, user_email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': db_user.email}, expires_delta=access_token_expires
    )
    await add_token(access_token, db)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/logout')
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    await del_token(token, db)
    return {'message': 'Successfully logged out', 'status': status.HTTP_200_OK}


@router.post('/register')
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create(user, db)


@router.get('/users', response_model=List[UserResponse])
async def get_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await read(db)


@router.patch('/update/{user_id:int}')
async def update_user(
        data: UserUpdate, user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await update(data, user_id, db)


@router.delete('/delete/{user_id:int}')
async def delete_user(
        user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete(user_id, db)
