import json
import time
import random

from twitchdrives.common import get_redis

redis = get_redis()

while True:
    redis.publish("tesla:state", json.dumps({
        "speed": random.randint(0, 420),
        "shift_state": random.choice("PRND"),
        "battery": random.randint(0, 101),
        "range": random.randint(0, 300),
    }))
    time.sleep(1)
