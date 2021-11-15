from twitchdrives.api.tesla import get_tesla
from twitchdrives.common import get_aioredis

class ActionBase:
    ACTION_NAME = None

    def __init__(self):
        self.redis = get_aioredis()

    async def get_state(self):
        state = {}

        global_state = await self.redis.hgetall("tesla:state:global")
        state.update(global_state or {})

        action_state = await self.redis.hgetall("tesla:state:" + self.ACTION_NAME)
        state.update(action_state or {})

        return state
