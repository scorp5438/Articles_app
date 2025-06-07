from backend.tests.conftest import db_session, app
from backend.api.v1.endpoints.users import router as users_router
from backend.db.session import get_db
from backend.tests.conftest import test_data
from backend.crud.user import get_user


async def test_get_users_not_admin(db_session, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(0)
    response = await client.get(f'{users_router.prefix}/users')
    data = response.json()

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'


async def test_get_users_admin(db_session, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client()
    response = await client.get(f'{users_router.prefix}/users')
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 4
    assert data[0].get('email') == 'test_user_1@mail.ru'
    assert data[1].get('full_name') == 'test_user_2'
    assert data[3].get('is_active')


async def test_get_profile(db_session, auth_client):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(1)
    response = await client.get(f'{users_router.prefix}/profile')
    data = response.json()

    assert response.status_code == 200
    assert data.get('email') == 'test_user_2@mail.ru'
    assert data.get('full_name') == 'test_user_2'
    assert data.get('conf_reg_link') is None


async def test_user_update_self(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user_data = {'email': 'new_test_email@mail.ru'}
    email_before_update = test_data.get('users')[1].email
    client = await auth_client(1)
    assert email_before_update == 'test_user_2@mail.ru'
    response = await client.patch(
        f'{users_router.prefix}/update/2',
        json=user_data,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    email_after_update = test_data.get('users')[1].email

    assert response.status_code == 200
    assert data.get('message') == 'Update successfully'
    assert data.get('status') == 200
    assert email_after_update == 'new_test_email@mail.ru'


async def test_update_other_user_by_not_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user_data = {'email': 'new_test_email@mail.ru'}
    email_before_update = test_data.get('users')[1].email
    client = await auth_client(0)

    response = await client.patch(
        f'{users_router.prefix}/update/2',
        json=user_data,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    email_after_update = test_data.get('users')[1].email

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'
    assert email_before_update == email_after_update


async def test_update_other_user_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user_data = {'email': 'new_test_email@mail.ru'}
    email_before_update = test_data.get('users')[1].email
    client = await auth_client(3)
    assert email_before_update == 'test_user_2@mail.ru'
    response = await client.patch(
        f'{users_router.prefix}/update/2',
        json=user_data,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    email_after_update = test_data.get('users')[1].email

    assert response.status_code == 200
    assert data.get('message') == 'Update successfully'
    assert data.get('status') == 200
    assert email_after_update == 'new_test_email@mail.ru'


async def test_update_user_not_exist_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user_data = {'email': 'new_test_email@mail.ru'}
    email_before_update = test_data.get('users')[1].email
    client = await auth_client(3)

    response = await client.patch(
        f'{users_router.prefix}/update/5',
        json=user_data,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    email_after_update = test_data.get('users')[1].email

    assert response.status_code == 404
    assert data.get('detail') == 'User not found'
    assert email_before_update == email_after_update


async def test_user_delete_self(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(1)
    users_before_delete = test_data.get('users')
    assert len(users_before_delete) == 4
    response = await client.delete(
        f'{users_router.prefix}/delete/2')
    data = response.json()
    users_after_delete = await get_user(db_session)

    assert response.status_code == 200
    assert data.get('message') == 'User deleted'
    assert data.get('status') == 200
    assert len(users_after_delete) == 3


async def test_delete_other_user_by_not_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(0)
    users_before_delete = test_data.get('users')
    assert len(users_before_delete) == 4

    response = await client.delete(
        f'{users_router.prefix}/delete/2')
    data = response.json()
    users_after_delete = await get_user(db_session)

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'
    assert len(users_after_delete) == 4


async def test_delete_other_user_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(3)
    users_before_delete = test_data.get('users')
    assert len(users_before_delete) == 4
    response = await client.delete(
        f'{users_router.prefix}/delete/2')
    data = response.json()
    users_after_delete = await get_user(db_session)

    assert response.status_code == 200
    assert data.get('message') == 'User deleted'
    assert data.get('status') == 200
    assert len(users_after_delete) == 3


async def test_delete_user_not_exist_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    client = await auth_client(3)
    users_before_delete = test_data.get('users')
    assert len(users_before_delete) == 4
    response = await client.delete(
        f'{users_router.prefix}/delete/5')
    data = response.json()
    users_after_delete = await get_user(db_session)

    assert response.status_code == 404
    assert data.get('detail') == 'User not found'
    assert len(users_after_delete) == 4
