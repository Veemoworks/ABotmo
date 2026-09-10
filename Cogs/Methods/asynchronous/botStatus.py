import discord, os, psutil
from discord.ext import tasks, commands
from Cogs.database import uptime
from Cogs.Methods.asynchronous.methods import crash
from Cogs.Methods.methods import log
from resources.variables import pid

# All bot status related things
@tasks.loop(minutes=3)
async def customStatus(bot: commands.Bot):
    try:
        # stat = f"Helping {len(bot.guilds)} {'servers' if len(bot.guilds) > 1 else 'server'}"
        stat = f"Currently being updated! Please expect bugs and some things not to work."
        await bot.change_presence(activity=discord.CustomActivity(name=stat))
        print(log(False, f"Successfully changed status with {len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}!"))
    except Exception as e:
        await crash(e)
        print(log(False, f"Failed to change status: {e}"))

@tasks.loop(minutes=1)
async def botStatus(bot: commands.Bot): uptime(True, bot.latency);

@tasks.loop(hours=1)
async def ramthing():
    p = psutil.Process()
    for process in psutil.process_iter():
        if process.name() == "WindowsTerminal.exe":
            p = process
            break
    usage = (psutil.Process(p.pid).memory_full_info().uss / (1024**2)) + (psutil.Process(pid).memory_full_info().uss / (1024**2))
    if usage >= 4000:
        os.system("cls")
        print(log(False, f"Cleared Console"))
    print(log(False, f"RAM Usage Report: {round((usage / 16000) * 100, 2)}% ({round(usage)}MB / 16000MB)"))