import asyncio
from sanic import Sanic
import json

from twitchdrives.common import get_aioredis

app = Sanic(name="twitchdrives_overlay")

@app.listener("before_server_start")
async def setup_redis(app, loop):
    app.redis = await get_aioredis()


app.static("/", "./index.html")
app.static("/static", "./static")

@app.websocket("/stream")
async def stream_tesla(request, ws):
    tesla_state = await app.redis.hgetall("tesla:state")
    print(tesla_state)
    await ws.send(json.dumps(tesla_state))
    while True:
        await asyncio.sleep(5)
