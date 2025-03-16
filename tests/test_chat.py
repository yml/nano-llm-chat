import json
from django.urls import reverse, resolve
from django.test import Client
from chat import AIModel, Message

def test_index():
    client = Client()
    url = reverse("index")  # Ensure you name or re-check the route in your urls.py
    response = client.get(url)
    assert response.status_code == 200

def test_get_messages():
    Message.objects.create(role="user", content="Hello user!")
    Message.objects.create(role="bot", content="Hello bot!")
    client = Client()
    # url = reverse("messages")  # Ensure you name or re-check the route in your urls.py
    url = "/api/messages"
    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) == 2

# def test_create_message():
#     client = Client()
#     url = reverse("create_message")

#     # Create an active model to avoid ValueError
#     AIModel.objects.create(provider="ollama", model="test-model", is_active=True)

#     post_data = {"content": "Hi from test!"}
#     response = client.post(url, post_data)
#     assert response.status_code == 200
#     # You can further inspect the streaming response and/or check the DB
#     assert Message.objects.filter(role="user", content="Hi from test!").exists()

