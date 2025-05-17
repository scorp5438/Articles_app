import pytest
from fastapi import HTTPException

from backend.crud.user import get_user, create, read, update, delete
from backend.tests.conftest import test_data, db_session
from backend.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_get_users(db_session, test_data):
    users = await get_user(db_session)
    user_by_id = await get_user(db_session, 1)
    user_by_email = await get_user(db_session, user_email='test_user_2@mail.ru')

    with pytest.raises(HTTPException) as e:
        await get_user(db_session, 5)

    assert len(users) == 4
    assert users[0].full_name == 'test_user_1'
    assert users[1].email == 'test_user_2@mail.ru'
    assert user_by_id.full_name == 'test_user_1'
    assert user_by_email.email == 'test_user_2@mail.ru'


@pytest.mark.asyncio
async def test_create_user(db_session, test_data):
    new_user = UserCreate(
        email='alex_77_90@mail.ru',
        password='Qwerty741',
        full_name='New Test User'
    )

    users_before = await get_user(db_session)
    response = await create(new_user, db_session)
    users_after = await get_user(db_session)

    assert len(users_before) == 4
    assert len(users_before) != len(users_after)
    assert response.get('message') == 'Successfully registered'
    assert response.get('status') == 201


@pytest.mark.asyncio
async def test_create_user_with_exist_email(db_session, test_data):
    new_user = UserCreate(
        email='test_user_1@mail.ru',
        password='Qwerty741',
        full_name='New Test User'
    )

    users_before = await get_user(db_session)
    with pytest.raises(HTTPException) as e:
        await create(new_user, db_session)
    users_after = await get_user(db_session)

    assert len(users_before) == len(users_after) == 4
    assert e.value.detail == 'Email already registered'
    assert e.value.status_code == 400


@pytest.mark.asyncio
async def test_read_user_list_by_staff(db_session, test_data):
    current_user = test_data.get('users')
    users = await read(db_session, current_user[3], user_list=True)

    assert len(users) == 4
    assert users[0].full_name == 'test_user_1'
    assert users[3].is_staff is True


@pytest.mark.asyncio
async def test_read_user_list_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')

    with pytest.raises(HTTPException) as e:
        await read(db_session, current_user[1], user_list=True)

    assert e.value.status_code == 403
    assert e.value.detail == 'You don`t have permission'


@pytest.mark.asyncio
async def test_read_user_profile_by_staff(db_session, test_data):
    current_user = test_data.get('users')
    user = await read(db_session, current_user[3])

    assert user.full_name == 'test_user_is_staff'
    assert user.is_staff is True


@pytest.mark.asyncio
async def test_read_user_profile_by_not_staff(db_session, test_data):
    current_user = test_data.get('users')
    user = await read(db_session, current_user[1])

    assert user.full_name == 'test_user_2'
    assert user.is_staff is False


@pytest.mark.asyncio
async def test_update_other_user_by_staff(db_session, test_data):
    user_id = 1

    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='new_test_user_1'
    )

    user_before_update = await get_user(db_session, user_id)
    assert user_before_update.full_name == 'test_user_1'

    response = await update(user_id, current_user[3], db_session, data)
    user_after_update = await get_user(db_session, user_id)

    assert response.get('message') == 'Update successfully'
    assert response.get('status') == 200
    assert user_after_update.full_name == 'new_test_user_1'


@pytest.mark.asyncio
async def test_update_user_by_self(db_session, test_data):
    user_id = 2

    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='new_test_user_2'
    )

    user_before_update = await get_user(db_session, user_id)
    assert user_before_update.full_name == 'test_user_2'

    response = await update(user_id, current_user[1], db_session, data)
    user_after_update = await get_user(db_session, user_id)

    assert response.get('message') == 'Update successfully'
    assert response.get('status') == 200
    assert user_after_update.full_name == 'new_test_user_2'


@pytest.mark.asyncio
async def test_update_user_other_user_by_not_staff(db_session, test_data):
    user_id = 3

    current_user = test_data.get('users')
    data = UserUpdate(
        full_name='new_test_user_3'
    )

    user_before_update = await get_user(db_session, user_id)
    assert user_before_update.full_name == 'test_user_3'
    with pytest.raises(HTTPException) as e:
        await update(user_id, current_user[0], db_session, data)

    user_after_update = await get_user(db_session, user_id)

    assert e.value.detail == 'You don`t have permission'
    assert e.value.status_code == 403
    assert user_after_update.full_name == 'test_user_3'


@pytest.mark.asyncio
async def test_delete_other_user_by_staff(db_session, test_data):
    user_id = 1

    current_user = test_data.get('users')

    users_before_update = await get_user(db_session)
    response = await delete(user_id, current_user[3], db_session)
    users_after_update = await get_user(db_session)

    assert len(users_before_update) == 4
    assert len(users_after_update) == 3
    assert response.get('message') == 'User deleted'
    assert response.get('status') == 200


@pytest.mark.asyncio
async def test_delete_other_user_by_self(db_session, test_data):
    user_id = 1

    current_user = test_data.get('users')

    users_before_update = await get_user(db_session)
    response = await delete(user_id, current_user[0], db_session)
    users_after_update = await get_user(db_session)

    assert len(users_before_update) == 4
    assert len(users_after_update) == 3
    assert response.get('message') == 'User deleted'
    assert response.get('status') == 200


@pytest.mark.asyncio
async def test_delete_other_user_by_not_self(db_session, test_data):
    user_id = 1

    current_user = test_data.get('users')

    users_before_update = await get_user(db_session)
    with pytest.raises(HTTPException) as e:
        await delete(user_id, current_user[1], db_session)
    users_after_update = await get_user(db_session)

    assert len(users_before_update) == len(users_after_update)
    assert e.value.status_code == 403
    assert e.value.detail == 'You don`t have permission'
