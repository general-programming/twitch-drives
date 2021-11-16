import asyncio
import os

import bottom

from twitchdrives.api.tesla import get_car
from twitchdrives.caractions.navigation import NavigationAction
from twitchdrives.exceptions import VehicleAsleep, VehicleInvalidShare
from twitchdrives.store.chat import ChatStore

nick = os.environ["TWITCH_USER"]
server = "irc.chat.twitch.tv"
password = os.environ["TWITCH_PASS"]
port = 6697

bot = bottom.Client(host=server, port=port, ssl=True)
chatstore = ChatStore()


@bot.on('CLIENT_CONNECT')
async def connect(**kwargs):
    print("connecting")
    bot.send('PASS', password=password)
    bot.send('NICK', nick=nick)
    bot.send('USER', user=nick,
             realname='https://github.com/numberoverzero/bottom')

    # Don't try to join channels until the server has
    # sent the MOTD, or signaled that there's no MOTD.
    print("waiting for motd")
    done, pending = await asyncio.wait(
        [bot.wait("RPL_ENDOFMOTD"),
         bot.wait("ERR_NOMOTD")],
        loop=bot.loop,
        return_when=asyncio.FIRST_COMPLETED
    )
    print("motd done")

    # Cancel whichever waiter's event didn't come in.
    for future in pending:
        future.cancel()

    bot.send('JOIN', channel="#" + nick)
    print("joined channel")


@bot.on("client_disconnect")
async def reconnect(**kwargs):
    await bot.connect()


@bot.on("ping")
def keepalive(message, **kwargs):
    bot.send("PONG", message=message)


@bot.on('PRIVMSG')
async def message(nick: str, target: str, message: str, **kwargs):
    """ Echo all messages """
    print(nick, target, message)
    await chatstore.add("twitch", message, nick, target)

    message = message.strip()
    if message.startswith("!info"):
        async with get_car() as car:
            try:
                car_details = await car.get_vehicle_data()
            except VehicleAsleep:
                bot.send("PRIVMSG", target=target, message="The car is in sleep mode. :(")
                return

            output = "{name} is at {charge}%, going {speed}mph. The temperature outside is {outside_temp}C. The temperature inside is {inside_temp}C. Car's version is {version}".format(
                name=car_details['vehicle_state']['vehicle_name'],
                charge=car_details['charge_state']['battery_level'],
                speed=car_details['drive_state']['speed'] or 0,
                inside_temp=car_details['climate_state']['inside_temp'],
                outside_temp=car_details['climate_state']['outside_temp'],
                version=car_details['vehicle_state']['car_version']
            )
            bot.send("PRIVMSG", target=target, message=output)
    elif message.startswith("!navigate"):
        try:
            destination = message.split("!navigate", 2)[1]
        except IndexError:
            return
        navigation = NavigationAction()

        try:
            await navigation.handle(destination)
            reply = f"Navigating to '{destination}'"
        except VehicleInvalidShare:
            reply = f"'{destination}' is not a valid destination."

        bot.send("PRIVMSG", target=target, message=reply)

bot.loop.create_task(bot.connect())
bot.loop.run_forever()
