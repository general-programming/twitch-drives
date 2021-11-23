from twitchdrives.api.tesla import get_tesla
from twitchdrives.common import get_aioredis, ctx_aioredis


class ActionBase:
    ACTION_NAME = None

    def __init__(self):
        self.redis = get_aioredis()

    async def get_state(self):
        state = {}

        with ctx_aioredis() as redis:
            global_state = await redis.hgetall("tesla:state:global")
            state.update(global_state or {})

            action_state = await redis.hgetall("tesla:state:" + self.ACTION_NAME)
            state.update(action_state or {})

        return state
