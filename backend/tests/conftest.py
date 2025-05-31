import requests

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import FastAPI
from async_asgi_testclient import TestClient
from pydantic import SecretStr

from backend.core.security import get_password_hash, generate_timestamp_link, create_access_token
from backend.db.models.user import User
from backend.db.models.article import Article
from backend.db.models.comment import Comment
from backend.db.session import Base
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.articles import router as articles_router
from backend.api.v1.endpoints.comments import router as comments_router
from backend.crud.user import add_token
from backend.core.config import CONF

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(comments_router)

TEST_DATABASE_URL = 'postgresql+asyncpg://test_user:test_password@localhost/test_db'


@pytest.fixture(scope='function')
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Создаем и возвращаем новую сессию
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()  # Откатываем несохраненные изменения

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def auth_client(db_session, test_data):
    async def _auth_client(user_index=3):
        test_user = test_data['users'][user_index]
        access_token = create_access_token({'sub': test_user.email})

        await add_token(access_token, db_session)

        return TestClient(
            app,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    return _auth_client


@pytest.fixture
async def test_data(db_session):
    test_user_hashed_password = get_password_hash('Qwerty741')
    full_link = generate_timestamp_link()
    rand_part, *_ = full_link.split('_')

    test_users = [
        User(
            email='test_user_1@mail.ru',
            hashed_password=test_user_hashed_password,
            full_name='test_user_1',
            conf_reg_link=None,
            is_active=True
        ),
        User(
            email='test_user_2@mail.ru',
            hashed_password=test_user_hashed_password,
            full_name='test_user_2',
            conf_reg_link=None,
            is_active=True
        ),
        User(
            email='test_user_3@mail.ru',
            hashed_password=test_user_hashed_password,
            full_name='test_user_3',
            conf_reg_link=rand_part,
            is_active=False
        ),
        User(
            email='test_user_is_staff@mail.ru',
            hashed_password=test_user_hashed_password,
            full_name='test_user_is_staff',
            conf_reg_link=None,
            is_active=True,
            is_staff=True
        )
    ]

    db_session.add_all(test_users)
    await db_session.flush()

    articles = [
        Article(
            title='Test Articles with user',
            content='Random test text',
            author_id=test_users[0].id,
        ),
        Article(
            title='Test Articles without user',
            content='Another test texts',
            author_id=None,
        )
    ]

    db_session.add_all(articles)
    await db_session.flush()

    comments = [
        Comment(
            content='The test comment 1 for article 1',
            article_id=1,
            author_id=1
        ),
        Comment(
            content='The other test comment for article 1',
            article_id=1,
            author_id=2
        ),
        Comment(
            content='The test comment 1 for article 2',
            article_id=2,
            author_id=4
        ),
    ]
    db_session.add_all(comments)
    await db_session.commit()

    for test_user in test_users:
        await db_session.refresh(test_user)

    for article in articles:
        await db_session.refresh(article)

    for comment in comments:
        await db_session.refresh(comment)

    return {'users': test_users, 'full_link': full_link}


@pytest.fixture(scope='function')
def override_smtp_config():
    original_config = {
        'MAIL_USERNAME': CONF.MAIL_USERNAME,
        'MAIL_PASSWORD': CONF.MAIL_PASSWORD,
        'MAIL_FROM': CONF.MAIL_FROM,
        'MAIL_PORT': CONF.MAIL_PORT,
        'MAIL_SERVER': CONF.MAIL_SERVER,
        'MAIL_STARTTLS': CONF.MAIL_STARTTLS,
        'MAIL_SSL_TLS': CONF.MAIL_SSL_TLS,
    }

    CONF.MAIL_USERNAME = ''
    CONF.MAIL_PASSWORD = SecretStr("")
    CONF.MAIL_FROM = 'test@example.com'
    CONF.MAIL_PORT = 1025
    CONF.MAIL_SERVER = 'localhost'
    CONF.MAIL_STARTTLS = False
    CONF.MAIL_SSL_TLS = False

    yield

    for key, value in original_config.items():
        setattr(CONF, key, value)


@pytest.fixture(scope='function')
def clear_mailhog():
    requests.delete('http://localhost:8025/api/v1/messages', timeout=1)
    yield
