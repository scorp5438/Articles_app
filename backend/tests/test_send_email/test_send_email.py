import asyncio
import pytest
import requests

from backend.schemas.user import UserForEmail
from backend.fast_api_email.fast_api_email import send_email
from backend.tests.conftest import override_smtp_config, clear_mailhog


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

    for _ in range(5):
        response = requests.get("http://localhost:8025/api/v2/messages")
        messages = response.json()
        if messages["items"]:
            break
        await asyncio.sleep(1)
    else:
        pytest.fail("Письмо не появилось в MailHog после 5 секунд ожидания")

    # response = requests.get('http://localhost:8025/api/v2/messages')
    messages = response.json()
    last_message = messages["items"][0]
    recipients = last_message.get('Content').get('Headers').get('To')
    subject = last_message["Content"]["Headers"]["Subject"]

    assert response.status_code == 200
    assert len(messages['items']) > 0
    assert test_user.email in recipients
    assert 'Test Email' in subject
