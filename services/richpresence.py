import os
import time

import teslapy
from pypresence import Presence

client_id = "907891789569073183"
RPC = Presence(client_id, pipe=0)
RPC.connect()


def rich():
    with teslapy.Tesla(os.environ["TESLA_EMAIL"]) as tesla:
        vehicles = tesla.vehicle_list()
        car = vehicles[0]

        while True:
            car_details = car.get_vehicle_data()
            bottom_text = f"{car_details['charge_state']['battery_level']}% charged"
            large_image = "parked"

            if car_details["state"] in ["offline", "asleep"]:
                state = "Parked"
            else:
                print(car_details["drive_state"]["speed"])
                if not car_details["drive_state"]["speed"]:
                    if car_details["charge_state"]["charging_state"] == "Charging":
                        state = "Charging"
                    else:
                        state = "Parked"
                else:
                    state = "Driving"
                    bottom_text = f"{car_details['drive_state']['speed']}mph"
                    large_image = "driving"

            print(car_details)

            RPC.update(
                large_image=large_image,
                large_text="image hover",
                details=state,
                state=bottom_text,
            )
            time.sleep(10)


rich()
