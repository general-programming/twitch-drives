import json
from twitchdrives.common import get_aioredis
from twitchdrives.constants import MAX_MESSAGES


class ChatStore:
    def __init__(self):
        self.redis = get_aioredis()

    async def add(self, source, message, nick, channel, **kwargs):
        payload = {
            "source": source,
            "username": nick,
            "channel": channel,
            "message": message,
            **kwargs
        }

        await self.redis.xadd("stream:chat", payload, maxlen=MAX_MESSAGES)
        await self.redis.publish("stream:chat", json.dumps({
            "chat": payload
        }))

    async def read(self, count: int = 25):
        messages = await self.redis.xrevrange("stream:chat", count=count)
        for message in messages[::-1]:
            data = message[1]
            # assuming that the message id is always { epoch_ms }-0
            data["timestamp"] = message[0].split("-")[0]
            yield data

    async def cleanup(self):
        await self.redis.close()
