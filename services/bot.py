import logging
import os
import time
from unicodedata import name

import nextcord
import redis
import teslapy
from nextcord.ext import commands

from twitchdrives.api.tesla_sync import get_tesla

logging.basicConfig(level=logging.INFO)
client = commands.Bot(command_prefix="t!")
tesla = get_tesla()
car = tesla.vehicle_list()[0]

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

@client.command(help="Car information")
async def info(ctx):
    car_details = car.get_vehicle_data()
    embed = nextcord.Embed(
        title=f"{car_details['vehicle_config']['car_type']} - {car_details['vehicle_state']['vehicle_name']}"
    )

    embed.add_field(
        name="Charge",
        value=f"{car_details['charge_state']['battery_level']}%",
        inline=True
    )

    embed.add_field(
        name="Speed",
        value=f"{car_details['drive_state']['speed'] or 0}mph",
        inline=True
    )

    embed.add_field(
        name="User Present?",
        value=car_details["vehicle_state"]["is_user_present"],
        inline=True
    )

    embed.add_field(
        name="Temperature (inside/outside)",
        value=f"{car_details['climate_state']['inside_temp']}C/{car_details['climate_state']['outside_temp']}C",
        inline=True
    )

    embed.set_footer(
        text=f"version {car_details['vehicle_state']['car_version']}"
    )

    await ctx.send(embed=embed)

@client.command(help="Navigate to a location")
async def navigate(ctx, *args):
    location = " ".join(args)

    car.command(
        "SEND_TO_VEHICLE",
        type="share_ext_content_raw",
        locale="en-US",
        value={
            "android.intent.extra.TEXT": location
        },
        timestamp_ms=round(time.time() * 1000)
    )
    await ctx.reply(f"Navigating to '{location}'")

# @client.command()
# async def honk(ctx):
#     car.command("HONK_HORN")
#     await ctx.send("<:honk:907977608434696212>")

@client.command(help="Wakes up the car")
async def wakeup(ctx):
    car.sync_wake_up()
    await ctx.send("Car is awake.")

client.run(os.environ["DISCORD_TOKEN"])
