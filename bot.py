import discord, os, platform, sys
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from Cogs.Methods.methods import crash
from Cogs.Methods.asynchronous.botEvents import command_error, app_command_error, kuma
from Cogs.Methods.asynchronous.botStatus import status
from Cogs.Methods.methods import handle_exception, log

load_dotenv()
with open("output.txt", "w") as f:
    f.write(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] \"Running bot.py\"...\n")
bot = commands.Bot(command_prefix=";;", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        cogs = [ "fun", "utils", "moderation", "server" ]
        for cog in cogs:
            await bot.load_extension(f"commands.{cog}")
        try:
            synced = await bot.tree.sync()
            thing = f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] ABOTMO ONLINE\n[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Logged in as {bot.user}\n[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Synced {len(synced)} commands\n[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] PyCord version: {discord.__version__}\n[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Python version: {platform.python_version()}\n[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Running on: {platform.system()} {platform.release()} ({os.name})"
            print("\033[92m" + thing)
            with open("output.txt", "a") as r:
                r.write(thing + "\n")
            cmds = await bot.tree.fetch_commands()
            for command in cmds:
                print(log(False, f"Command {command.name} (</{command.name}:{command.id}>) Registered!"))
        except Exception as e:
            print(log(True, f"Sync Error: {e}"))
        bot.loop.create_task(status(bot))
        # kuma.start(bot)
    except Exception as e:
        await crash(e)
        print(log(True,f"Error occurred in starting up the bot!: {e}"))

@bot.event
async def on_command_error_event(ctx, error):
    await command_error(ctx, error)


@bot.tree.error
async def on_app_command_error_event(interaction, error):
    await app_command_error(interaction, error)


sys.excepthook = handle_exception

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))