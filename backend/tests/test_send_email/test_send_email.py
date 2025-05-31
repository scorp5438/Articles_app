import asyncio
import os

import pytest
import requests

from backend.schemas.user import UserForEmail
from backend.fast_api_email.fast_api_email import send_email
from backend.tests.conftest import override_smtp_config, clear_mailhog


import socket

def check_localhost_connection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def test_mailhog_connection():
    assert check_localhost_connection(8025), "MailHog is not reachable on localhost:8025"

def test_environment():
    assert os.getenv('VIRTUAL_ENV') is not None, "Not running in a virtual environment"
    print("Running in virtual environment:", os.getenv('VIRTUAL_ENV'))
    print("GITHUB_ACTIONS:", os.getenv('GITHUB_ACTIONS'))

import logging

logging.basicConfig(level=logging.INFO)

def test_mailhog_connection2():
    logging.info("Checking connection to MailHog on localhost:8025")
    assert check_localhost_connection(8025), "MailHog is not reachable on localhost:8025"


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
        link='https://test.com'
    )

    await asyncio.sleep(5)

    response = requests.get('http://localhost:8025/api/v2/messages')
    messages = response.json()
    last_message = messages['items'][0]
    recipients = last_message.get('Content').get('Headers').get('To')
    subject = last_message['Content']['Headers']['Subject']

    assert response.status_code == 200
    assert len(messages['items']) > 0
    assert test_user.email in recipients
    assert 'Test Email' in subject
