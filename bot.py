import discord, os, sys, logging, asyncio
from discord.ext import commands
from Cogs.BotEvents import load
from datetime import datetime
from dotenv import load_dotenv
from Cogs.Methods.asynchronous.methods import get_prefix
from Cogs.Methods.methods import handle_exception, log, close_bot

debugging = False
startup = datetime.now()
load_dotenv()
sys.excepthook = handle_exception

if __name__ == "__main__":
    with open("output.txt", "w") as f:
        f.write("")
        print(log(False, "Initilizaing..."))
    if debugging:
        with open("debug.txt", "w") as f:
            f.write("")
    # for sharded client (1000+ servers)
    # bot = commands.AutoShardedBot
    bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all(), max_messages=500)
    asyncio.run(load(bot))
    bot.run(os.getenv("TOKEN"), log_handler=logging.FileHandler(filename='debug.txt', encoding='utf-8', mode='a') if debugging else None, log_level=logging.DEBUG)