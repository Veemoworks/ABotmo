import requests, json, discord, sqlite3, asyncio, random
from DataBases.database import server_prefix, modlogchannel
from resources.links import warm
from resources.dictionaries import headers
from datetime import datetime

# All asynchronous methods

# Send embed to a webhook whenever an error occurs
async def crash(error):
    print(f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] Fatal error occurred: {error}")
    try:
        data = {
            "embeds": [
                {
                    "title": "BOT ERROR!",
                    "description": str(error)[:1024],
                    "color": 0x9B59B6,
                    "thumbnail": {
                        "url": warm,
                    },
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        res = requests.post(
            "https://discord.com/api/webhooks/1399754937491128420/krs4046qAiczly-uy8XAzJN2o5ADaFnZLjklXig6msVui7_I92sl_fafzelbk2xD9Qkj",
            data=json.dumps(data), headers=headers)
        print(f"\033[92m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] {res.status_code}: Error message sent successfully.")
    except Exception as e:
        print(f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] Failed to send error message: {e}")

# Get bot prefix for a guild
async def get_prefix(bot, message):
    if not message.guild:
        return ";;"

    prefix = server_prefix(False, message.guild)
    return prefix or ";;"

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
    embed.add_field(name="Info", value=f"{data[4].lower().capitalize()}: {data[2]}")
    embed.set_footer(text=f"ID: {user.id}")
    embed.timestamp = datetime.now()
    if data[4] == "WARNING" or data[4] == "BAN":
        embed.add_field(name="Message", value=f"{f"{data[3]}\n" if not data[3] == None else ""}User now has {rows} modlogs.")
    await channel.send(embed=embed)

# for /silly and /evil
async def calculator(interaction: discord.Interaction, type: str, mention: str):
    rand = random.randint(0, 115)
    if rand > 100:
        danr = rand - 100
        rand = rand - danr

    if rand == 100:
        dynevil = f"__**PURE {type.upper()}!!**__"
    elif rand >= 75:
        dynevil = f"**{type.upper()}!!**"
    elif rand >= 50:
        dynevil = f"{type.upper()}!"
    elif rand >= 25:
        dynevil = f"{type}!"
    else:
        dynevil = f"{type}."

    evil = discord.Embed(title=f"{type.capitalize()} Calculator",
                         description=f"This **{type.upper()}** calculator can determine anyone's {type} level...",
                         color=discord.Color.yellow())
    await interaction.response.send_message(embed=evil)
    await asyncio.sleep(2)
    evil.add_field(name=".", value="")
    await interaction.edit_original_response(embed=evil)
    await asyncio.sleep(1)
    evil.set_field_at(0, name=". .", value="")
    await interaction.edit_original_response(embed=evil)
    await asyncio.sleep(1)
    evil.set_field_at(0, name=". . .", value="")
    await interaction.edit_original_response(embed=evil)
    await asyncio.sleep(1)
    evil.remove_field(0)
    await interaction.edit_original_response(embed=evil)
    await asyncio.sleep(2)
    evil.add_field(name="", value=f"{mention} is {rand}% {dynevil}")
    await interaction.edit_original_response(embed=evil)
