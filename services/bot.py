import logging
import os
import random
import sys
import traceback

import nextcord
from nextcord.ext import commands

from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.navigation import NavigationAction
from twitchdrives.caractions.vote import VoteAction
from twitchdrives.exceptions import CommandCooldown, VehicleAsleep, VehicleInvalidShare
from twitchdrives.store.chat import ChatStore

logging.basicConfig(level=logging.INFO)
client = commands.Bot(command_prefix="t!")
chatstore = ChatStore()
TESLA_CHANNEL = int(os.environ["DISCORD_TESLA_CHANNEL"])


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.content and message.channel.id == TESLA_CHANNEL:
        await chatstore.add(
            "discord",
            message.content,
            nick=message.author.name,
            channel=message.channel.name,
            discord_author_id=message.author.id,
            discord_channel_id=message.channel.id,
        )
    await client.process_commands(message)


if "TEST" in os.environ:

    @client.event
    async def on_command_error(ctx, error):
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )
        if ctx.author.id != 66153853824802816:
            return

        embed = nextcord.Embed(
            description="An error happened running this command",
            color=nextcord.Colour.red(),
        ).set_author(
            name="Something happened",
            icon_url="https://nepeat.github.io/assets/icons/error.png",
        )

        # Owner extra info
        embed.add_field(
            name=random.choice(
                [
                    "How you fucked up",
                    "Blame nepeat",
                    "Hellback (Most recent failure last)",
                    "lol",
                ]
            ),
            value=f"```{traceback.format_exception(type(error), error, error.__traceback__)}```",
        )

        return await ctx.send(embed=embed)


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
        inline=True,
    )

    embed.add_field(
        name="Speed",
        value=f"{car_details['drive_state']['speed'] or 0}mph",
        inline=True,
    )

    embed.add_field(
        name="User Present?",
        value=car_details["vehicle_state"]["is_user_present"],
        inline=True,
    )

    embed.add_field(
        name="Temperature (inside/outside)",
        value=f"{car_details['climate_state']['inside_temp']}C/{car_details['climate_state']['outside_temp']}C",
        inline=True,
    )

    embed.set_footer(text=f"version {car_details['vehicle_state']['car_version']}")

    await ctx.send(embed=embed)


@client.command(help="Navigate to a location")
async def navigate(ctx, *args):
    location = " ".join(args)
    navigation = NavigationAction()

    try:
        await navigation.handle(location)
        reply = f"Navigating to '{location}'"
    except VehicleInvalidShare:
        reply = f"'{location}' is not a valid destination."
    except CommandCooldown as e:
        reply = f"Command is on cooldown, pls hold on for {e.cooldown} seconds!"

    await ctx.send(nextcord.utils.escape_mentions(reply))


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
