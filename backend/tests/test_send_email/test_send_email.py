import pytest
import requests

from backend.schemas.user import UserForEmail
from backend.fast_api_email.fast_api_email import send_email
from backend.tests.conftest import override_smtp_config, clear_mailhog
from backend.tasks.email_tasks import send_email_task

@pytest.mark.asyncio
async def test_send_email_real_smtp(override_smtp_config, clear_mailhog):
    test_user = UserForEmail(
        email='test_user_13@mail.ru',
        full_name='New Test User'
    )

    await send_email(
        user=test_user,
        subject='Test Email',
        template_name='reg_confirm.html',
        link='https://example.com'
    )

    response = requests.get('http://localhost:8025/api/v2/messages')
    messages = response.json()
    last_message = messages['items'][0]
    recipients = last_message.get('Content').get('Headers').get('To')
    subject = last_message.get('Content').get('Headers').get('Subject')

    assert response.status_code == 200
    assert len(messages['items']) > 0
    assert test_user.email in recipients
    assert 'Test Email' in subject


@pytest.mark.asyncio
async def test_send_email_task_real(override_smtp_config, clear_mailhog):
    test_user = UserForEmail(
        email='test_receiver@example.com',
        full_name='Test User'
    )

    await send_email_task.apply(args=(test_user, 'Test Email', 'reg_confirm.html', 'https://example.com')).get()

    response = requests.get('http://localhost:8025/api/v2/messages')
    messages = response.json()
    last_message = messages['items'][0]
    recipients = last_message.get('Content').get('Headers').get('To')
    subject = last_message.get('Content').get('Headers').get('Subject')

    assert response.status_code == 200
    assert len(messages['items']) > 0
    assert test_user.email in recipients
    assert 'Test Email' in subject