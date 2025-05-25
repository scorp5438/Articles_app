from sqlalchemy.future import select
from async_asgi_testclient import TestClient

from backend.tests.conftest import db_session, app
from backend.api.v1.endpoints.comments import router as comments_router
from backend.db.session import get_db
from backend.tests.conftest import test_data
from crud.comments import read


async def test_get_comments(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    response = await TestClient(app).get(f'{comments_router.prefix}/1')
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get('content') == 'The test comment 1 for article 1'
    assert data[1].get('content') == 'The other test comment for article 1'


async def test_create_comment_by_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'content': '123321 32g1 3s2fg1 3s21g',
        'article_id': 1
    }
    comments_before = await read(1, db_session)
    assert len(comments_before) == 2
    client = await auth_client(0)

    response = await client.post(
        f'{comments_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    comments_after= await read(1, db_session)

    assert response.status_code == 200
    assert data.get('message') == 'Comment successfully added'
    assert len(comments_after) == 3

async def test_create_comment_by_not_auth_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'content': '123321 32g1 3s2fg1 3s21g',
        'article_id': 1
    }
    comments_before = await read(1, db_session)
    assert len(comments_before) == 2

    response = await TestClient(app).post(
        f'{comments_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    comments_after = await read(1, db_session)

    assert response.status_code == 401
    assert data.get('detail') == 'Not authenticated'
    assert len(comments_after) == 2


async def test_create_comment_by_not_active_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'content': '123321 32g1 3s2fg1 3s21g',
        'article_id': 1
    }
    comments_before = await read(1, db_session)
    assert len(comments_before) == 2
    client = await auth_client(2)

    response = await client.post(
        f'{comments_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    comments_after= await read(1, db_session)

    assert response.status_code == 403
    assert data.get('detail') == 'You need to confirm email'
    assert len(comments_after) == 2


async def test_delete_comment_by_self(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    comments_before = await read(1, db_session)
    assert len(comments_before) == 2
    client = await auth_client(0)

    response = await client.delete(f'{comments_router.prefix}/delete/1')
    data = response.json()
    comments_after= await read(1, db_session)

    assert response.status_code == 200
    assert data.get('message') == 'Comment deleted'
    assert len(comments_after) == 1


async def test_delete_other_comment_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    comments_before = await read(1, db_session)
    assert len(comments_before) == 2
    client = await auth_client(3)

    response = await client.delete(f'{comments_router.prefix}/delete/1')
    data = response.json()
    comments_after= await read(1, db_session)

    assert response.status_code == 200
    assert data.get('message') == 'Comment deleted'
    assert len(comments_after) == 1


async def test_delete_other_comment_by_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    comments_before = await read(1, db_session)
    assert len(comments_before) == 2
    client = await auth_client(2)

    response = await client.delete(f'{comments_router.prefix}/delete/1')
    data = response.json()
    comments_after= await read(1, db_session)

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'
    assert len(comments_after) == 2