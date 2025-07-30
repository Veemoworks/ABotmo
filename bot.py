import discord, os, platform, Cogs.Methods.asynchronous.botStatus, sys
from discord.ext import commands
from dotenv import load_dotenv
from Cogs.Methods.asynchronous.botEvents import on_command_error, on_app_command_error
from Cogs.Methods.methods import handle_unhandled_exception

load_dotenv()
bot = commands.Bot(command_prefix=";;", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        cogs = [ "commands.fun", "commands.utils", "commands.moderation", ]
        for cog in cogs:
            await bot.load_extension(cog)
        try:
            synced = await bot.tree.sync()
            cmds = await bot.tree.fetch_commands()
            for command in cmds:
                print(f"Registered Slash Command {command.name} (MD: </{command.name}:{command.id}>)")
            print(f"------------\nABOTMO ONLINE", f"Logged in as {bot.user}", f"✅ Synced {len(synced)} commands", f"PyCord version: {discord.__version__}",
                  f"Python version: {platform.python_version()}",
                  f"Running on: {platform.system()} {platform.release()} ({os.name})\n------------", sep="\n------------\n")
        except Exception as e:
            print(f"❌ Sync Error: {e}")
        bot.loop.create_task(Cogs.Methods.asynchronous.botStatus.status(bot))
    except Exception as e:
        print(f"Error occurred in starting up the bot!: {e}")

@bot.event
async def on_command_error_event(ctx, error):
    await on_command_error(bot, ctx, error)

@bot.tree.error
async def on_app_command_error_event(interaction, error):
    await on_app_command_error(bot, interaction, error)

sys.excepthook = handle_unhandled_exception

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))