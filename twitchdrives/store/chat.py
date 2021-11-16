from twitchdrives.common import get_aioredis
from twitchdrives.constants import MAX_MESSAGES

class ChatStore:
    def __init__(self):
        self.redis = get_aioredis()

    async def add(self, source, message, nick, channel):
        await self.redis.xadd("stream:chat", {
            "source": source,
            "username": nick,
            "channel": channel,
            "message": message,
        }, maxlen=MAX_MESSAGES)

    async def cleanup(self):
        await self.redis.close()
