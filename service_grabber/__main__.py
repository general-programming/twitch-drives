import asyncio
import json

from twitchdrives.api.tesla import Vehicle, get_tesla
from twitchdrives.common import get_aioredis
from twitchdrives.exceptions import VehicleAsleep, VehicleTimeout


class VehicleGrabber:
    def __init__(self):
        self.running = True
        self.tasks = []
        self.redis = get_aioredis()

    async def job_poller(self, vehicle: Vehicle):
        while self.running:
            await asyncio.sleep(10)

            try:
                vehicle_data = await vehicle.get_vehicle_data()
            except VehicleTimeout:
                print("vehicle poll timed out")
                continue
            except VehicleAsleep:
                print("vehicle asleep")
                await vehicle.wake_up()
                continue

            await self.push_data("poll", vehicle_data)

    async def socket_poller(self, vehicle: Vehicle):
        async for event in vehicle.stream():
            await self.push_data("socket", event)

    async def push_data(self, event_source: str, event: dict, save: bool = True):
        if save:
            await self.redis.lpush("tesla:events:" + event_source, json.dumps(event))

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
        await self.redis.hset("tesla:state", mapping=to_push)
        await self.redis.publish("tesla:state", json.dumps(to_push))

    async def main(self):
        self.tesla = await get_tesla()

        # Get the vehicle and wake it up.
        vehicles = await self.tesla.vehicles
        vehicle = vehicles[0]
        await vehicle.wake_up()

        # Launch tasks.
        self.tasks.append(asyncio.create_task(self.job_poller(vehicle)))
        self.tasks.append(asyncio.create_task(self.socket_poller(vehicle)))

        # Infinitely wait until Control + C
        try:
            await asyncio.gather(*self.tasks)
        except KeyboardInterrupt:
            self.running = False
            for task in self.tasks:
                task.cancel()
            await self.redis.close()
            await self.tesla.aclose()


if __name__ == "__main__":
    grabber = VehicleGrabber()
    asyncio.run(grabber.main())
