from async_asgi_testclient import TestClient
from sqlalchemy.future import select

from backend.tests.conftest import db_session, app
from backend.api.v1.endpoints.auth import router as auth_router
from backend.db.session import get_db
from backend.tests.conftest import test_data
from backend.db.models.user import Token


async def test_register_success(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    test_user = {
        'email': 'test_user_7@mail.ru',
        'password': 'Qwerty741',
        'full_name': 'Test_user'
    }
    async with TestClient(app) as client:
        response = await client.post(f'{auth_router.prefix}/register', json=test_user)
        data = response.json()

        assert response.status_code == 200
        assert data.get('message') == 'Successfully registered'
        assert data.get('status') == 201


async def test_activation_profile(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = test_data.get('full_link')
    current_users = test_data.get('users')
    async with TestClient(app) as client:
        response = await client.get(f'{auth_router.prefix}/reg-confirm/{full_link}')
        data = response.json()

        assert response.status_code == 200
        assert current_users[2].is_active == True
        assert current_users[2].conf_reg_link is None
        assert data.get('message') == 'User activate'


async def test_activation_profile_token_expired(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = test_data.get('full_link')
    current_users = test_data.get('users')

    async with TestClient(app) as client:
        response = await client.get(f'{auth_router.prefix}/reg-confirm/{full_link[:-1]}0')
        data = response.json()

        assert response.status_code == 408
        assert current_users[2].is_active == False
        assert current_users[2].conf_reg_link is not None
        assert data.get('detail') == 'Token expired'


async def test_activation_profile_token_invalid(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    full_link = 'invalidtoken_123456798_1'
    current_users = test_data.get('users')

    async with TestClient(app) as client:
        response = await client.get(f'{auth_router.prefix}/reg-confirm/{full_link}')
        data = response.json()

        assert response.status_code == 404
        assert data.get('detail') == 'Confirm token invalid'


async def test_login_success(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    auth_user = {
        'username': 'test_user_1@mail.ru',
        'password': 'Qwerty741',
    }
    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form=auth_user,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )

        data = response.json()

        assert response.status_code == 200
        assert 'access_token' in data
        assert len(data.get('access_token')) > 0
        assert data.get('token_type') == 'bearer'


async def test_login_user_not_exists(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    auth_user = {
        'username': 'test_user_5@mail.ru',
        'password': 'Qwerty741',
    }
    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form=auth_user,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )

        data = response.json()

        assert response.status_code == 401
        assert data.get('detail') == 'User not found'


async def test_login_user_invalid_password(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    auth_user = {
        'username': 'test_user_1@mail.ru',
        'password': 'Qwerty147',
    }
    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form=auth_user,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )

        data = response.json()

        assert response.status_code == 401
        assert data.get('detail') == 'Incorrect login or password'


async def test_logout(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    auth_user = {
        'username': 'test_user_1@mail.ru',
        'password': 'Qwerty741',
    }
    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form=auth_user,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        token = response.json().get('access_token')

        response = await client.post(
            f'{auth_router.prefix}/logout',
            headers={'Authorization': f'Bearer {token}'},
        )

        data = response.json()

        is_token = (await db_session.execute(select(Token).filter(Token.token == token))).scalars().first()

        assert response.status_code == 200
        assert is_token is None
        assert data.get('message') == 'Successfully logged out'


async def test_get_link(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    user = test_data.get('users')[2]

    async with TestClient(app) as client:
        response = await client.post(
            f'{auth_router.prefix}/login',
            form={'username': user.email, 'password': 'Qwerty741'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        token = response.json().get('access_token')

        response = await client.get(
            f'{auth_router.prefix}/get_link',
            headers={'Authorization': f'Bearer {token}'}
        )

        data = response.json()

        assert response.status_code == 200
        assert data.get('message') == 'link was sent'
