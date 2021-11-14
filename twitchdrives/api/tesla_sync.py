import json
import os

import teslapy

from twitchdrives.common import get_redis


def get_tesla() -> teslapy.Tesla:
    redis = get_redis()
    def cache_loader():
        try:
            return json.loads(redis.get("tesla:tokens"))
        except TypeError:
            return {}

    def cache_dumper(data: dict):
        redis.set("tesla:tokens", json.dumps(data))

    return teslapy.Tesla(
        os.environ["TESLA_EMAIL"],
        cache_loader=cache_loader,
        cache_dumper=cache_dumper,
    )
