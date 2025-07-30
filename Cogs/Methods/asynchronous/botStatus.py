import discord, random, asyncio

async def status(bot):
    check = None
    while True:
        guild = [guild async for guild in bot.fetch_guilds(limit=200)]
        activities = [discord.Activity(type=discord.ActivityType.watching, name=f"{len(guild)} {"servers" if len(guild) > 1 else "server"}"),]
                      # discord.Activity(type=discord.ActivityType.listening, name="ABotmo Radio"),
                      # discord.Game("VeraVeemoSMP"),
                      # discord.Streaming(name="Console", url="https://github.com/VeraVeemo/ABotmo"),
                      # discord.Activity(type=discord.ActivityType.competing, name="a Command Race")]
        activity = random.choice(activities)
        if check == activity:
            continue
        check = activity
        await bot.change_presence(activity=activity)
        await asyncio.sleep(30)