import pytest
from fastapi import HTTPException

from backend.crud.user import get_user
from backend.tests.conftest import test_data_art, db_session

@pytest.mark.asyncio
async def test_get_users(db_session, test_data_art):
    users = await get_user(db_session)
    user_by_id = await get_user(db_session, 1)
    user_by_email = await get_user(db_session, user_email='test_user_2@mail.ru')


    with pytest.raises(HTTPException) as e:
        await get_user(db_session, 3)

    with pytest.raises(HTTPException) as e_2:
        await get_user(db_session, user_email='test_user_3@mail.ru')



    assert len(users) == 2
    assert users[0].full_name == 'test_user_1'
    assert users[1].email == 'test_user_2@mail.ru'

    assert user_by_id.full_name == 'test_user_1'
    assert user_by_email.email == 'test_user_2@mail.ru'

    assert e.value.status_code == 404
    assert e_2.value.detail == 'user not found'