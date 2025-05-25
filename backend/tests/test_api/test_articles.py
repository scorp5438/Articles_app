from sqlalchemy.future import select
from async_asgi_testclient import TestClient

from backend.tests.conftest import db_session, app
from backend.api.v1.endpoints.articles import router as articles_router
from backend.db.session import get_db
from backend.tests.conftest import test_data
from backend.db.models import Article
from backend.crud.articles import get_article


async def test_get_articles(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    response = await TestClient(app).get(f'{articles_router.prefix}/')
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get('title') == 'Test Articles with user'
    assert 'Another test texts' in data[1].get('content')


async def test_get_article(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    response = await TestClient(app).get(f'{articles_router.prefix}/1')
    data = response.json()

    assert response.status_code == 200
    assert data.get('title') == 'Test Articles with user'


async def test_get_article_not_exist(db_session, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    response = await TestClient(app).get(f'{articles_router.prefix}/3')
    data = response.json()

    assert response.status_code == 404
    assert data.get('detail') == 'Article not found'


async def test_create_article_by_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'New test article by user 1',
        'content': '9485948ug 8-98g -9f8 s-f8bu pisdfbu'
    }

    client = await auth_client(0)
    response = await client.post(
        f'{articles_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles = (await db_session.execute(select(Article))).scalars().all()

    assert response.status_code == 200
    assert data.get('message') == 'Article created'
    assert len(articles) == 3


async def test_create_article_no_auth(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'New test article by no auth user',
        'content': '9485948ug 8-98g -9f8 s-f8bu pisdfbu'
    }

    response = await TestClient(app).post(
        f'{articles_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles = (await db_session.execute(select(Article))).scalars().all()

    assert response.status_code == 401
    assert data.get('detail') == 'Not authenticated'
    assert len(articles) == 2


async def test_create_article_no_activate(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'New test article by user 1',
        'content': '9485948ug 8-98g -9f8 s-f8bu pisdfbu'
    }

    client = await auth_client(2)
    response = await client.post(
        f'{articles_router.prefix}/create',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles = (await db_session.execute(select(Article))).scalars().all()

    assert response.status_code == 403
    assert data.get('detail') == 'You need to confirm email'
    assert len(articles) == 2


async def test_update_self_article_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'Update title',
    }
    articles_title_after = await get_article(db_session, 1)
    assert articles_title_after.title == 'Test Articles with user'
    client = await auth_client(0)
    response = await client.patch(
        f'{articles_router.prefix}/update/1',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles_title_before = await get_article(db_session, 1)

    assert response.status_code == 200
    assert data.get('message') == 'Article updated'
    assert articles_title_before.title == 'Update title'


async def test_update_other_article_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'Update title',
    }
    articles_title_after = await get_article(db_session, 2)
    client = await auth_client(0)
    response = await client.patch(
        f'{articles_router.prefix}/update/2',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles_title_before = await get_article(db_session, 2)

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'
    assert articles_title_before.title == articles_title_after.title


async def test_update_other_article_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'Update title',
    }
    articles_title_after = await get_article(db_session, 1)
    assert articles_title_after.title == 'Test Articles with user'
    client = await auth_client(3)
    response = await client.patch(
        f'{articles_router.prefix}/update/1',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()
    articles_title_before = await get_article(db_session, 1)

    assert response.status_code == 200
    assert data.get('message') == 'Article updated'
    assert articles_title_before.title == 'Update title'


async def test_update_article_not_exist_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session
    data_article = {
        'title': 'Update title',
    }

    client = await auth_client(3)
    response = await client.patch(
        f'{articles_router.prefix}/update/3',
        json=data_article,
        headers={'Content-Type': 'application/json'},
    )
    data = response.json()

    assert response.status_code == 404
    assert data.get('detail') == 'Article not found'


async def test_delete_self_article_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    articles_after = await get_article(db_session)
    assert len(articles_after) == 2
    client = await auth_client(0)
    response = await client.delete(f'{articles_router.prefix}/delete/1')
    data = response.json()
    articles_before = await get_article(db_session)

    assert response.status_code == 200
    assert data.get('message') == 'Article deleted'
    assert len(articles_before) == 1


async def test_delete_other_article_base_user(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    articles_after = await get_article(db_session)
    assert len(articles_after) == 2
    client = await auth_client(0)
    response = await client.delete(f'{articles_router.prefix}/delete/2')
    data = response.json()
    articles_before = await get_article(db_session)

    assert response.status_code == 403
    assert data.get('detail') == 'You don`t have permission'
    assert len(articles_before) == 2


async def test_delete_other_article_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    articles_after = await get_article(db_session)
    assert len(articles_after) == 2
    client = await auth_client(3)
    response = await client.delete(f'{articles_router.prefix}/delete/1')
    data = response.json()
    articles_before = await get_article(db_session)

    assert response.status_code == 200
    assert data.get('message') == 'Article deleted'
    assert len(articles_before) == 1


async def test_delete_article_not_exist_by_admin(db_session, auth_client, test_data):
    app.dependency_overrides[get_db] = lambda: db_session

    articles_after = await get_article(db_session)
    assert len(articles_after) == 2
    client = await auth_client(3)
    response = await client.delete(f'{articles_router.prefix}/delete/3')
    data = response.json()
    articles_before = await get_article(db_session)

    assert response.status_code == 404
    assert data.get('detail') == 'Article not found'
    assert len(articles_before) == 2
