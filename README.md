# Nano LLM chat

This project is an adaptation of the [pydantic-ai chat example](https://ai.pydantic.dev/examples/chat-app/#running-the-example) where I replaced pydantic-ai with mirascope and fastAPI with Nanodjango.

`uv` is the package manager and the main dependencies for this project are uv, nanodjango, mirascope.


## Start the app
Before starting, you need to export the `OPENAI_API_KEY` environment variable by running the following command in your terminal:
```
export OPENAI_API_KEY=your_api_key
```

Start the chat app. 

```
uv run nanodjango run chat.py 
```

open http://localhost:8000 in your browser to access the chat interface.


## Django Admin


[Create an instance](http://localhost:8000/wall-garden/chat/aimodel/) of an `AI model`.

Example:

* provider: OpenAI
* model: gpt-3.5-turbo
* stream: True
* Is Active: True


## Run the test suite

```
uv run pytest
```