import sys, asyncio, traceback, discord, sqlite3
from datetime import datetime
from discord import app_commands
from Cogs.Methods.asynchronous.methods import crash
from DataBases.database import server_roles, modlogchannel

# Regular functions here

# Permission check on commands
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

# Exception handle for sys exceptions
def handle_exception(exc_type, exc_value, exc_traceback, bot):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    asyncio.run_coroutine_threadsafe(crash(Exception(error_msg)), bot.loop)

# Log to a file
def log(error, msg):
    with open("output.txt", "a") as f:
        f.write(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] {"[ERROR   ]" if error else "[INFO    ]"} {msg}\n")
    if error:
        return f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] {msg}"
    else:
        return f"\033[92m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] {msg}"

# Log to a file and close the bot
def close_bot():
    with open("output.txt", "a") as f:
        f.write(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Bot session was ended.\n")
    with open(r"Files\last_shutdown.txt", "w") as f:
        f.write(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    with open(r"Files\ABotmo_ping.txt", "w") as f:
        f.write("Offline")

# log things to modlog channel
async def logChannel(bot, interaction, data, user):
    temp = modlogchannel(False, interaction.guild)
    if temp == None:
        return
    channel = await bot.fetch_channel(int(temp))
    con = sqlite3.connect("DataBases/modlogs.db")
    cur = con.cursor()
    cur.execute(f"""
            SELECT * FROM '{interaction.guild.id}';
    """)
    rows = len(cur.fetchall())
    embed = discord.Embed(color=discord.Color.yellow())
    embed.set_author(name=f"CASE {rows} | {data[4]} | {user.name}", icon_url=user.avatar.url)
    embed.add_field(name="User", value=f"{user.mention}")
    embed.add_field(name="Moderator", value=f"{interaction.user.mention}")
    embed.add_field(name="Info", value=f"{data[4]}: {data[2]}")
    embed.set_footer(text=f"ID: {user.id}")
    embed.timestamp = datetime.now()
    if data[4] == "WARNING" or data[4] == "BAN":
        embed.add_field(name="Message", value=f"{f"{data[3]}\n" if not data[3] == None else ""}User now has {rows} modlogs.")
    await channel.send(embed=embed)