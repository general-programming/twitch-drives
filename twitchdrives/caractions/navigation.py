import time
from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.base import ActionBase


class NavigationAction(ActionBase):
    ACTION_NAME = "navigation"

    async def handle(self, location: str):
        async with get_car() as car:
            await car.command(
                "SEND_TO_VEHICLE",
                type="share_ext_content_raw",
                locale="en-US",
                value={
                    "android.intent.extra.TEXT": location
                },
                timestamp_ms=round(time.time() * 1000)
            )
