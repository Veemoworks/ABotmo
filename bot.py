import discord, os, platform, sys
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from Cogs.Methods.methods import crash
from Cogs.Methods.asynchronous.botEvents import command_error, app_command_error, message
from Cogs.Methods.asynchronous.botStatus import status, kuma, bot_ping
from Cogs.Methods.asynchronous.methods import get_prefix
from Cogs.Methods.methods import handle_exception, log, close_bot

# Load .env, clear old output.txt, and initalize the bot
load_dotenv()
with open("output.txt", "w") as f:
    f.write(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Initializing...\n")
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
done = False

# Bot event for when bot starts up
@bot.event
async def on_ready():
    global done
    try:
        try:
            if not done:
                # Load cogs
                cogs = ["fun", "utils", "moderation", "server"]
                for cog in cogs:
                    await bot.load_extension(f"commands.{cog}")
                # Sync bot tree.
                synced = await bot.tree.sync()
                thing = (f"\033[92m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] ABOTMO ONLINE\n"
                         f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Logged in as {bot.user}\n"
                         f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Synced {len(synced)} commands\n"
                         f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] PyCord version: {discord.__version__}\n"
                         f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Python version: {platform.python_version()}\n"
                         f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Running on: {platform.system()} {platform.release()} ({os.name})\n")
                print(thing, end="")
                with open("output.txt", "a") as r:
                    r.write("[" + thing.lstrip("\033[92m"))
                cmds = await bot.tree.fetch_commands()
                for command in cmds:
                    print(log(False, f"Command {command.name} (</{command.name}:{command.id}>) Registered!"))
                # Bot Loops
                # Start status cycle loop
                bot.loop.create_task(status(bot))
                # Start logging bot ping to a file
                bot_ping.start(bot)
                # Start uptime kuma pings
                kuma.start(bot)
                done = True
        except Exception as e:
            print(log(True, f"Sync Error: {e}"))
    except Exception as e:
        await crash(e)
        print(log(True,f"Error occurred in starting up the bot!: {e}"))

# prefix command error
@bot.event
async def on_command_error_event(ctx, error):
    await command_error(ctx, error)

# Slash command error
"""@bot.tree.error
async def on_app_command_error_event(interaction, error):
    await app_command_error(interaction, error)
"""
# On message events
@bot.event
async def on_message(msg):
    await message(msg)

    await bot.process_commands(msg)

# System exception
sys.excepthook = handle_exception

# Run bot
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
    close_bot()
