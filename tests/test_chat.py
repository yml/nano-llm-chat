import json
from unittest.mock import Mock

import pytest

from django.urls import reverse
from mirascope.llm.call_response_chunk import CallResponseChunk

from chat import AIModel, Message


def test_index(client):
    url = reverse("index")  # Ensure you name or re-check the route in your urls.py
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_messages(client):
    Message.objects.create(role="user", content="Hello user!")
    Message.objects.create(role="bot", content="Hello bot!")
    url = reverse("ninja:messages")
    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) == 2


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_create_message(async_client, monkeypatch):
    USER_MSG = "Hello from test!"
    BOT_MSG = "Hello from the bot!"

    async def fake_respond_to_user_with_active(*args, **kwargs):
        async def fake_response(user_message: str):
            async def stream():
                chunk = Mock(spec=CallResponseChunk)
                chunk.content = BOT_MSG
                yield (chunk, None)

            return stream()

        return fake_response

    # Patch the original function to use our custom function during the test
    monkeypatch.setattr(
        "chat.respond_to_user_with_active", fake_respond_to_user_with_active
    )

    url = reverse("ninja:create_message")

    # Create an active model to avoid ValueError
    _ = await AIModel.objects.acreate(
        provider="fake", model="test-model", is_active=True
    )

    post_data = {"content": USER_MSG}
    response = await async_client.post(url, post_data)
    assert response.status_code == 200

    # Consume the response stream and validate the output
    response_chunks = []
    async for chunk in response.streaming_content:
        try:
            response_chunks.extend(json.loads(chunk))
        except json.decoder.JSONDecodeError:
            print(f"Failed to decode JSON: {chunk}")
            continue
    assert len(response_chunks) == 2
    assert response_chunks[0]["role"] == "user"
    assert response_chunks[0]["content"] == USER_MSG
    assert response_chunks[1]["role"] == "bot"
    assert response_chunks[1]["content"] == BOT_MSG

    # check if the messages were saved in the database
    msg_results = []
    async for msg in Message.objects.filter():
        msg_results.append(msg)
    assert len(msg_results) == 2
    assert msg_results[0].role == "user"
    assert msg_results[0].content == USER_MSG
    assert msg_results[1].role == "bot"
    assert msg_results[1].content == BOT_MSG
