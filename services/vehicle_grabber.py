import asyncio
from twitchdrives.api.tesla import get_tesla

class VehicleGrabber:
    @property
    @staticmethod
    def loop():
        return asyncio.get_event_loop()

    async def main(self):
        self.tesla = await get_tesla()

        vehicles = await self.tesla.vehicles
        vehicle = vehicles[0]

        await vehicle.wake_up()
        await vehicles[0].stream()

if __name__ == "__main__":
    grabber = VehicleGrabber()
    asyncio.run(grabber.main())

