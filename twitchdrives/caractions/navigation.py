import time

from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.base import ActionBase
from twitchdrives.common import ctx_aioredis
from twitchdrives.exceptions import CommandCooldown


class NavigationAction(ActionBase):
    ACTION_NAME = "navigation"

    async def handle(self, location: str):
        async with ctx_aioredis() as redis:
            cooldown_ttl = await redis.ttl("tesla:navicooldown")
            if cooldown_ttl >= 0:
                raise CommandCooldown(cooldown_ttl)

            async with get_car() as car:
                await redis.setex("tesla:navicooldown", 10, "1")
                await car.command(
                    "SEND_TO_VEHICLE",
                    type="share_ext_content_raw",
                    locale="en-US",
                    value={"android.intent.extra.TEXT": location},
                    timestamp_ms=round(time.time() * 1000),
                )
