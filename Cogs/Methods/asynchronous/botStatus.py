import discord, asyncio
from Cogs.Methods.asynchronous.methods import crash
from Cogs.Methods.methods import log

async def status(bot):
    while True:
        try:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}"))
            print(log(False, f"Successfully changed status with {len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}!"))
        except Exception as e:
            await crash(e)
            print(log(False, f"Failed to change status: {e}"))
        await asyncio.sleep(180)