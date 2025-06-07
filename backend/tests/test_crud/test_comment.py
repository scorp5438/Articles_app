import pytest
from fastapi import HTTPException

from backend.crud.comments import create, read, delete
from backend.tests.conftest import test_data, db_session
from backend.schemas.comment import CommentCreate


@pytest.mark.asyncio
async def test_create_comment(db_session, test_data):
    article = CommentCreate(
        content='New comment create in test',
        article_id=2
    )
    current_user = test_data.get('users')

    response = await create(current_user[1], article, db_session)

    comments = await read(2, db_session)

    assert response.get('message') == 'Comment successfully added'
    assert response.get('status') == 201
    assert comments[-1].content == 'New comment create in test'


@pytest.mark.asyncio
async def test_create_comment_by_not_active(db_session, test_data):
    article = CommentCreate(
        content='New comment create in test',
        article_id=1
    )
    current_user = test_data.get('users')

    with pytest.raises(HTTPException) as e:
        await create(current_user[2], article, db_session)

    comments = await read(2, db_session)

    assert e.value.status_code == 403
    assert e.value.detail == 'You need to confirm email'
    assert comments[-1].content != 'New comment create in test'


@pytest.mark.asyncio
async def test_read_comment(db_session, test_data):
    comments = await read(1, db_session)

    assert len(comments) == 2
    assert comments[0].content == 'The test comment 1 for article 1'
    assert comments[1].author_name == 'test_user_2'


@pytest.mark.asyncio
async def test_delete_comment_by_self(db_session, test_data):
    comment_id = 1
    current_user = test_data.get('users')
    comments_before_delete = await read(1, db_session)
    assert len(comments_before_delete) == 2
    response = await delete(comment_id, current_user[0], db_session)
    comments_after_delete = await read(1, db_session)

    assert len(comments_after_delete) == 1
    assert response.get('message') == 'Comment deleted'
    assert response.get('status') == 200


@pytest.mark.asyncio
async def test_delete_comment_not_by_self(db_session, test_data):
    comment_id = 2
    current_user = test_data.get('users')

    comments_before_delete = await read(1, db_session)
    assert len(comments_before_delete) == 2

    with pytest.raises(HTTPException) as e:
        await delete(comment_id, current_user[0], db_session)

    comments_after_delete = await read(1, db_session)

    assert len(comments_after_delete) == 2
    assert e.value.status_code == 403
    assert e.value.detail == 'You don`t have permission'


@pytest.mark.asyncio
async def test_delete_other_comment_by_staff(db_session, test_data):
    comment_id = 1
    current_user = test_data.get('users')
    comments_before_delete = await read(1, db_session)
    assert len(comments_before_delete) == 2
    response = await delete(comment_id, current_user[3], db_session)
    comments_after_delete = await read(1, db_session)

    assert len(comments_after_delete) == 1
    assert response.get('message') == 'Comment deleted'
    assert response.get('status') == 200