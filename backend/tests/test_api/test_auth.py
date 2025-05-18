from backend.tests.conftest import db_session, app
from backend.api.v1.endpoints.auth import router as auth_router
from backend.db.session import get_db
from backend.tests.conftest import client

async def test_register_success(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    test_user = {
        'email': 'alex_77_90@mail.ru',
        'password': 'Qwerty741',
        'full_name': 'Test_user'
    }
    async with client as c:
        response = await c.post(f'{auth_router.prefix}/register', json=test_user)
        data = response.json()

        assert response.status_code == 200
        assert data["message"] == 'Successfully registered'
        assert data["status"] == 201





















