import sys, asyncio, traceback, discord
from datetime import datetime
from discord import app_commands
from Cogs.Methods.asynchronous.methods import crash
from DataBases.database import server_roles

def permission_check():
    async def predicate(interaction: discord.Interaction):
        user = interaction.guild.get_member(interaction.user.id)
        allowed_roles = server_roles(False, interaction)
        if not allowed_roles:
            await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
            return False
        for role in user.roles:
            if str(role.id) in allowed_roles:
                return True
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return False

    return app_commands.check(predicate)

def handle_exception(exc_type, exc_value, exc_traceback, bot):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    asyncio.run_coroutine_threadsafe(crash(Exception(error_msg)), bot.loop)

def log(error, msg):
    with open("output.txt", "a") as f:
        f.write(msg + "\n")
    if error:
        return f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] {msg}"
    else:
        return f"\033[92m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] {msg}"