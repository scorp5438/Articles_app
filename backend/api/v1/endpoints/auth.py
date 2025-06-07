from datetime import timedelta
from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError

from backend.core.security import (verify_password,
                                   create_access_token,
                                   oauth2_scheme,
                                   get_current_user)
from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.db.session import get_db
from backend.schemas.user import (Token,
                                  UserCreate)

from backend.crud.user import (create,
                               get_user,
                               add_token,
                               del_token,
                               activate)
from backend.db.models import User
from backend.crud.user import send_link

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
            detail='User not found'
        )
    try:
        verify_password(form_data.password, db_user.hashed_password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect login or password',
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


@router.get('/reg-confirm/{full_link}')
async def reg_confirm(
        full_link: str,
        db: Session = Depends(get_db)
):
    return await activate(full_link, db)


@router.get('/get_link')
async def get_link(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await send_link(current_user, db)
    return {'message': 'link was sent'}
