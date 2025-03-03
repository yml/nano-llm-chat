import json
import logging
import sys
from datetime import datetime
from typing import List

from django.db import models
from django.http import StreamingHttpResponse
from mirascope import Messages, llm
from nanodjango import Django

# Set up logging for async diagnostics
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = Django(
    ADMIN_URL="wall-garden/",
    ALLOWED_HOSTS=["*"],
    DEBUG=True,
    NINJA_DEFAULT_THROTTLE_RATES={"anon": "5/minute"},
)


@llm.call(provider="openai", model="gpt-3.5-turbo", stream=True)
async def respond_to_user(user_message: str) -> Messages.Type:
    return Messages.User(user_message)


@app.admin
class AIModel(models.Model):
    model = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider}:{self.model}"

    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"


@app.admin
class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content}"


class MessageIn(app.ninja.Schema):
    content: str


class MessageOut(MessageIn):
    id: int
    role: str
    created_at: datetime


@app.route("/")
async def index(request):
    return app.render(request, "chat.html", {"title": "Home"})


@app.api.get("/messages", response=List[MessageOut])
def get_messages(request):
    return Message.objects.all()


@app.api.post("/messages")
async def create_message(request, message: app.ninja.Form[MessageIn]):
    async def stream_messages():
        user_message = await Message.objects.acreate(
            role="user", content=message.content
        )
        yield (
            json.dumps([
                json.loads(
                    MessageOut(
                        id=user_message.id,
                        role=user_message.role,
                        content=user_message.content,
                        created_at=user_message.created_at,
                    ).model_dump_json()
                )
            ])
        )

        bot_response = ""
        stream = await respond_to_user(user_message.content)
        async for chunk, _ in stream:
            if not bot_response and chunk.content:
                bot_response = chunk.content
                bot_message = await Message.objects.acreate(
                    role="bot", content=chunk.content
                )

            elif chunk.content:
                bot_response += chunk.content
                yield (
                    json.dumps([
                        json.loads(
                            MessageOut(
                                id=bot_message.id,
                                role=bot_message.role,
                                content=bot_response,
                                created_at=bot_message.created_at,
                            ).model_dump_json()
                        )
                    ])
                )
            yield "<==Split==>"
        bot_message.content = bot_response
        await bot_message.asave()

    return StreamingHttpResponse(stream_messages(), content_type="text/event-stream")
