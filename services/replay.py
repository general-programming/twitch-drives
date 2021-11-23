import json
import time
from twitchdrives.common import get_redis


redis = get_redis()


def push_data(event_source: str, event: dict):
    to_push = {"_event_source": event_source}

    # Pull info from event.vehicle_state
    vehicle_state = event.get("vehicle_state", {})
    if vehicle_state:
        to_push["odometer"] = vehicle_state["odometer"]
        to_push["timestamp"] = vehicle_state["timestamp"]

    # Pull info from event.drive_state
    drive_state = event.get("drive_state", {})
    if drive_state:
        to_push["speed"] = drive_state.get("speed") or 0
        to_push["latitude"] = drive_state["latitude"]
        to_push["longitude"] = drive_state["longitude"]
        to_push["shift_state"] = drive_state["shift_state"] or "P"
        to_push["heading"] = drive_state["heading"]
        to_push["power"] = drive_state["power"]

    # Pull info from event.charge_state
    charge_state = event.get("charge_state", {})
    if charge_state:
        to_push["battery"] = charge_state["battery_level"]
        to_push["range"] = charge_state["battery_range"]

    # streaming events.
    if "speed" in event:
        to_push["speed"] = event["speed"] or 0

    if "shift_state" in event:
        to_push["shift_state"] = event["shift_state"] or "P"

    stream_events = {
        "odometer": "odometer",
        "est_lat": "latitude",
        "est_lng": "longitude",
        "soc": "battery",
        "est_range": "range",
        "timestamp": "timestamp",
        "heading": "heading",
        "power": "power",
    }

    for event_name, push_name in stream_events.items():
        if event_name in event:
            to_push[push_name] = event[event_name]

    print(event_source, to_push)
    # await self.redis.hset("tesla:state", mapping=to_push)
    redis.publish("tesla:state", json.dumps(to_push))


for item in redis.lrange("tesla:events:socket", 0, -1):
    item = json.loads(item)
    if "drive_state" in item:
        if (
            item["drive_state"]["shift_state"]
            and item["drive_state"]["shift_state"] != "P"
        ):
            push_data("replay", item)
            time.sleep(0.10)
    elif item["shift_state"] and item["shift_state"] != "P":
        push_data("replay", item)
        time.sleep(0.01)
