import logging
import os
import sys

import nextcord
import random
import traceback
from nextcord.ext import commands
from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.navigation import NavigationAction
from twitchdrives.caractions.vote import VoteAction
from twitchdrives.exceptions import VehicleAsleep

logging.basicConfig(level=logging.INFO)
client = commands.Bot(command_prefix="t!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

@client.command(help="Car information")
async def info(ctx):
    async with get_car() as car:
    try:
        car_details = await car.get_vehicle_data()
    except VehicleAsleep:
        await ctx.send("Vehicle is asleep. :(")
        return

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
    navigation = NavigationAction()

    await navigation.handle(location)
    await ctx.reply(f"Navigating to '{location}'")

@client.command()
async def vote(ctx, vote_type: str):
    vote_action = VoteAction()
    print(await vote_action.handle(vote_type))

# @client.command()
# async def honk(ctx):
#     car = await get_car()
#     await car.command("HONK_HORN")
#     await ctx.send("<:honk:907977608434696212>")

@client.command(help="Wakes up the car")
async def wakeup(ctx):
    async with get_car() as car:
    await car.wake_up()
    await ctx.send("Car is awake.")

client.run(os.environ["DISCORD_TOKEN"])
