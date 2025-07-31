import discord, asyncio

async def status(bot):
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}"))
        await asyncio.sleep(30)