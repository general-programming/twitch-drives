import os

from twitchio.ext import commands

from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.navigation import NavigationAction
from twitchdrives.exceptions import VehicleAsleep, VehicleInvalidShare, CommandCooldown
from twitchdrives.store.chat import ChatStore

nick = os.environ["TWITCH_USER"]
server = "irc.chat.twitch.tv"
port = 6697

chatstore = ChatStore()


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(
            token=os.environ["TWITCH_PASS"], prefix="!", initial_channels=["#" + nick]
        )

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")

    async def event_message(self, message):
        if message.author:
            author_name = message.author.name
        else:
            author_name = self.nick

        await chatstore.add(
            source="twitch",
            message=message.content,
            nick=author_name,
            channel=message.channel.name,
        )
        print(author_name, message.channel.name, message.content)

        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def info(self, ctx: commands.Context):
        async with get_car() as car:
            try:
                car_details = await car.get_vehicle_data()
            except VehicleAsleep:
                await ctx.send("The car is in sleep mode. :(")
                return

            output = "{name} is at {charge}%, going {speed}mph. The temperature outside is {outside_temp}C. The temperature inside is {inside_temp}C. Car's version is {version}".format(
                name=car_details["vehicle_state"]["vehicle_name"],
                charge=car_details["charge_state"]["battery_level"],
                speed=car_details["drive_state"]["speed"] or 0,
                inside_temp=car_details["climate_state"]["inside_temp"],
                outside_temp=car_details["climate_state"]["outside_temp"],
                version=car_details["vehicle_state"]["car_version"],
            )

            await ctx.send(output)

    @commands.command()
    async def navigate(self, ctx: commands.Context, *args):
        location = " ".join(args)
        navigation = NavigationAction()

        try:
            await navigation.handle(location)
            reply = f"Navigating to '{location}'"
        except VehicleInvalidShare:
            reply = f"'{location}' is not a valid destination."
        except CommandCooldown as e:
            reply = f"Command is on cooldown, pls hold on for {e.cooldown} seconds!"

        await ctx.send(reply)


bot = Bot()
bot.run()
