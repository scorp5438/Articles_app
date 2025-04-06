from datetime import timedelta
from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.security import (verify_password,
                                   ACCESS_TOKEN_EXPIRE_MINUTES,
                                   create_access_token,
                                   oauth2_scheme)
from backend.db.session import get_db
from backend.schemas.user import (Token,
                                  UserCreate)

from backend.crud.user import (create,
                               get_user,
                               add_token,
                               del_token)

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
