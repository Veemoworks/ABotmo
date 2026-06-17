import requests, json, discord, asyncio, random, os, dotenv
from Cogs.database import server_settings, server_channels, webhooks
from resources.links import warm
from resources.dictionaries import headers
from datetime import datetime
dotenv.load_dotenv(".env")

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
            os.getenv("LOGWEBHOOK"),
            data=json.dumps(data), headers=headers)
        print(f"\033[92m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] {res.status_code}: Error message sent successfully.")
    except Exception as e:
        print(f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] Failed to send error message: {e}")

# Get bot prefix for a guild
async def get_prefix(bot, message):
    if not message.guild:
        return ";;"

    prefix = server_settings(False, message.guild, "prefix")
    return prefix or ";;"

# log things to modlog channel
async def logChannel(bot, interaction, data: list, user, amt):
    if data[0] == interaction.guild.id:
        data.pop(0)
    if data[-1] == data[-2]:
        data.pop(-1)
    embed = discord.Embed(color=discord.Color.yellow())
    case = server_settings(data[4] == "MODLOG REMOVAL", interaction.guild, "casenum")
    embed.set_author(name=f"CASE {case} | {data[4]} | {user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.add_field(name="User:", value=f"{user.mention}")
    embed.add_field(name="Moderator:", value=f"{interaction.user.mention}")
    embed.add_field(name="Info:", value=f"{"" if data[4] in ["MESSAGE", "MODLOG REMOVAL"] else "Reason: "}{data[2]}\n{"" if data in ["MESSAGE"] else f"User now has {amt} modlogs."}")
    embed.set_footer(text=f"LOG ID: {data[-1]}")
    if data[4] in [ "WARNING", "BAN", "KICK", "MUTE" ] and not data[3] is None:
        embed.add_field(name="Message:", value=data[3])
    elif data[4] in [ "MODLOG REMOVAL" ]:
        embed.add_field(name="Reason:", value=data[3])

    await event(bot, interaction.guild, "modlog", user, embed)

async def sendCase(interaction: discord.Interaction, data, user, amt):
    try:
        embed = discord.Embed(title=f"You have recieved a **{data[4]}** in __**{interaction.guild.name}**__!", description=f"CASE {server_settings(False, interaction.guild, "casenum")}", color=discord.Color.brand_red())
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_author(name=f"{interaction.guild.name} | {interaction.guild.id}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name="Reason:", value=data[2], inline=False)
        if not data[3] == None:
            embed.add_field(name="Mod Message:", value=data[3], inline=False)
        embed.add_field(name="Modlogs:", value=amt, inline=False)
        embed.set_footer(text='Use "/mylogs" to see your log count anytime in any server')
        embed.timestamp = datetime.now()

        await user.send(embed=embed)
    except discord.Forbidden or discord.HTTPException as e:
        ogMsg = await interaction.original_response()
        await interaction.edit_original_response(content=f"{ogMsg.content}\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {e}")
    except Exception:
        pass

# for /silly and /evil
async def calculator(interaction: discord.Interaction, ctype: str, mention: str):
    rand = random.randint(0, 115)
    if rand > 100:
        rand = 100

    if rand >= 100:
        dynevil = f"__**PURE {ctype.upper()}!!**__"
    elif rand >= 75:
        dynevil = f"**{ctype.upper()}!!**"
    elif rand >= 50:
        dynevil = f"{ctype.upper()}!"
    elif rand >= 25:
        dynevil = f"{ctype}!"
    else:
        dynevil = f"{ctype}."

    evil = discord.Embed(title=f"{ctype.capitalize()} Calculator",
                         description=f"This **{ctype.upper()}** calculator can determine anyone's {ctype} level...",
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

async def event(bot, guild, eventtype, ref, embed):
    channel = server_channels(False, guild, eventtype)
    if not channel:
        return
    channel = bot.get_channel(int(channel))
    allhooks = await channel.webhooks()
    webhook = None
    for webhk in allhooks:
        temp = webhooks(False, guild, [channel.id, webhk.id])
        if temp:
            webhook = temp
            break
    if webhook == None:
        try:
            newwebhook = await channel.create_webhook(name="ABotmo Logs", reason="Logging for ABotmo")
        except:
            return
        webhooks(True, guild, [newwebhook.id, newwebhook.token, channel.id])
        webhook = [newwebhook.id, newwebhook.token]
    embed.timestamp = datetime.now()
    if not embed.footer:
        embed.set_footer(text=f"{eventtype.capitalize()} ID: {ref.id}")
    resp = requests.post(f"https://discord.com/api/webhooks/{webhook[0]}/{webhook[1]}", json={ "avatar_url": bot.user.avatar.url, "embeds": [embed.to_dict()]}, headers=headers)
    if not resp.ok:
        print(f"\033[31m[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR   ] An error occured in sending an event!: {resp.status_code}: {resp.content}")

