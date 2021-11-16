import asyncio
import json

from sanic import Sanic

from twitchdrives.common import get_aioredis
from twitchdrives.store.chat import ChatStore

app = Sanic(name="twitchdrives_overlay")

@app.listener("before_server_start")
async def setup_redis(app, loop):
    app.redis = await get_aioredis()


app.static("/", "./index.html")
app.static("/static", "./static")

@app.websocket("/stream")
async def stream_tesla(request, ws):
    # return latest chat messages
    chat_store = ChatStore()
    async for message in chat_store.read():
        await ws.send(json.dumps({
            "chat": message
        }))

    # return latest tesla state
    tesla_state = await app.redis.hgetall("tesla:state")
    print(tesla_state)
    await ws.send(json.dumps(tesla_state))

    async with app.redis.pubsub(ignore_subscribe_messages=True) as pubsub:
        await pubsub.subscribe("tesla:state")
        await pubsub.subscribe("stream:chat")
        while True:
            message = await pubsub.get_message(timeout=1.0)
            if message:
                await ws.send(message["data"])
