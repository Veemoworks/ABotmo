import discord, os, platform, sys
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from Cogs.Methods.methods import crash
from Cogs.Methods.asynchronous.botEvents import command_error, app_command_error
from Cogs.Methods.asynchronous.botStatus import status
from Cogs.Methods.methods import handle_exception

load_dotenv()
bot = commands.Bot(command_prefix=";;", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        cogs = [ "fun", "utils", "moderation", "server" ]
        for cog in cogs:
            await bot.load_extension(f"commands.{cog}")
        try:
            synced = await bot.tree.sync()
            print(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] ABOTMO ONLINE",
                  f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Logged in as {bot.user}",
                  f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Synced {len(synced)} commands",
                  f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] PyCord version: {discord.__version__}",
                  f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Python version: {platform.python_version()}",
                  f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Running on: {platform.system()} {platform.release()} ({os.name})", sep="\n")
            cmds = await bot.tree.fetch_commands()
            for command in cmds:
                print(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Command {command.name} (</{command.name}:{command.id}>) Registered!", sep="\n")
        except Exception as e:
            raise Exception(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR    ] Sync Error: {e}")
        bot.loop.create_task(status(bot))
    except Exception as e:
        await crash(e)
        raise Exception(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR    ] Error occurred in starting up the bot!: {e}")

@bot.event
async def on_command_error_event(ctx, error):
    await command_error(ctx, error)


@bot.tree.error
async def on_app_command_error_event(interaction, error):
    await app_command_error(interaction, error)


sys.excepthook = handle_exception

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))