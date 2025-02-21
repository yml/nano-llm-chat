# Nano LLM chat

This project is an adaptation of the [pydantic-ai chat example](https://ai.pydantic.dev/examples/chat-app/#running-the-example) where I replaced pydantic-ai with mirascope and fastAPI with Nanodjango.



## Start the app
Before starting, you need to export the `OPENAI_API_KEY` environment variable by running the following command in your terminal:
```
export OPENAI_API_KEY=your_api_key
```

Start the chat app. 

```
uv run nanodjango run chat.py 
```

