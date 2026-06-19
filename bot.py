import os, asyncio, datetime, discord.ext, dotenv
from Cogs.BotEvents import load
from Cogs.Methods.asynchronous.methods import get_prefix

startup = datetime.datetime.now()

if __name__ == "__main__":
    dotenv.load_dotenv()
    with open("output.txt", "w") as f:
        msg = f"[{startup.strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Initilizaing..."
        f.write(msg + "\n")
        f.close()
    print(msg)
    bot = discord.ext.commands.Bot(get_prefix, intents=discord.Intents.all(), max_messages=500)
    asyncio.run(load(bot))
    bot.run(os.getenv("TOKEN"), log_handler=None)