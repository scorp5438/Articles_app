import pytest
from fastapi import HTTPException

from backend.crud.articles import get_article
from backend.tests.conftest import test_data_art, db_session


@pytest.mark.asyncio
async def test_get_articles(db_session, test_data_art):
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


