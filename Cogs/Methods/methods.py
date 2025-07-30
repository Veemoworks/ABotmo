import sys, asyncio, traceback, discord
from Cogs.Methods.asynchronous.methods import crash
from DataBases.database import server_settings

def permission_check():
    async def predicate(interaction: discord.Interaction):
        user = interaction.guild.get_member(interaction.user.id)
        roles = server_settings(False, interaction)
        for role in user.roles:
            for check in roles:
                check = check.strip("(", ")", "'")
                if check in role:
                    return True
        return False

def handle_exception(exc_type, exc_value, exc_traceback, bot):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    asyncio.run_coroutine_threadsafe(crash(Exception(error_msg)), bot.loop)