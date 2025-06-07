import pytest
from fastapi import HTTPException

from backend.crud.articles import get_article, create, read, update, delete
from backend.tests.conftest import test_data, db_session
from backend.schemas.article import ArticleUpdate, ArticleCreate


@pytest.mark.asyncio
async def test_get_articles(db_session, test_data):
    articles = await get_article(db_session)
    article_by_id = await get_article(db_session, 1)

    with pytest.raises(HTTPException) as e:
        await get_article(db_session, 3)

    assert len(articles) == 2
    assert articles[0].title == 'Test Articles with user'
    assert articles[1].author_id is None
    assert article_by_id.content == 'Random test text'
    assert article_by_id.author_id == 1
    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_create_articles(db_session, test_data):
    article = ArticleCreate(
        title='New article create in test',
        content='Anything text sor article'
    )
    current_user = test_data.get('users')

    response = await create(current_user[1], article, db_session)
    articles = await read(db_session)

    assert len(articles) == 3
    assert articles[2].title == 'New article create in test'
    assert response.get('message') == 'Article created'
    assert response.get('status') == 201


@pytest.mark.asyncio
async def test_create_articles_by_not_is_active(db_session, test_data):
    article = ArticleCreate(
        title='New article create in test',
        content='Anything text sor article'
    )
    current_user = test_data.get('users')

    count_before_create = await read(db_session)
    with pytest.raises(HTTPException) as e:
        await create(current_user[2], article, db_session)
    count_after_create = await read(db_session)

    assert len(count_before_create) == len(count_after_create)
    assert e.value.status_code == 403
    assert e.value.detail == 'You need to confirm email'


@pytest.mark.asyncio
async def test_read_articles(db_session, test_data):
    articles = await read(db_session)

    assert len(articles) == 2
    assert articles[0].title == 'Test Articles with user'
    assert articles[1].author_name == 'Удаленный пользователь'


@pytest.mark.asyncio
async def test_read_article_into_id(db_session, test_data):
    article_id = 1
    articles = await read(db_session, article_id)

    assert articles.title == 'Test Articles with user'
    assert articles.author_name == 'test_user_1'


@pytest.mark.asyncio
async def test_read_article_into_id_not_exist(db_session, test_data):
    article_id = 3

    with pytest.raises(HTTPException) as e:
        await read(db_session, article_id)

    assert e.value.status_code == 404
    assert e.value.detail == 'Article not found'


@pytest.mark.asyncio
async def test_update_articles(db_session, test_data):
    article_id = 1
    data = ArticleUpdate(
        content='A new content after update'
    )
    current_user = test_data.get('users')
    articles = await update(article_id, current_user[0], db_session, data)

    update_article = await read(db_session)

    assert articles.get('message') == 'Article updated'
    assert articles.get('status') == 200
    assert 'A new content after update' in update_article[0].content


@pytest.mark.asyncio
async def test_update_articles_not_by_author(db_session, test_data):
    article_id = 1
    data = ArticleUpdate(
        content='A new content after update'
    )
    current_user = test_data.get('users')

    article_before_update = await read(db_session)
    with pytest.raises(HTTPException) as e:
        await update(article_id, current_user[1], db_session, data)
    article_after_update = await read(db_session)

    assert article_before_update[0].title == article_after_update[0].title
    assert e.value.status_code == 403
    assert e.value.detail == 'You don`t have permission'


@pytest.mark.asyncio
async def test_delete_articles(db_session, test_data):
    article_id = 1
    current_user = test_data.get('users')
    count_before_delete = await read(db_session)
    response = await delete(article_id, current_user[0], db_session)
    count_after_delete = await read(db_session)

    assert response.get('message') == 'Article deleted'
    assert response.get('status') == 200
    assert len(count_before_delete) == 2
    assert len(count_after_delete) == 1


@pytest.mark.asyncio
async def test_delete_articles_not_by_author(db_session, test_data):
    article_id = 2
    current_user = test_data.get('users')
    count_before_delete = await read(db_session)
    with pytest.raises(HTTPException) as e:
        await delete(article_id, current_user[0], db_session)
    count_after_delete = await read(db_session)

    assert len(count_before_delete) == len(count_after_delete)
    assert e.value.status_code == 403
    assert e.value.detail == 'You don`t have permission'
