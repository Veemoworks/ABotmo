import sys, asyncio, traceback, discord, numpy as np, requests, json, os
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from discord import app_commands
from Cogs.Methods.asynchronous.methods import crash
from resources.dictionaries import kirk
from DataBases.database import server_settings
load_dotenv(".env")

# Regular functions here
def imgcol_gen(hex_color: str):
    h = hex_color.lstrip('#')
    temp_path = f"Files/icon_{h}.png"
    if not os.path.exists(temp_path):
        t = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        target_rgb = np.array(t, dtype=np.float32)
        img = Image.open("Files/icon.png").convert('RGBA')
        img.thumbnail((256, 256), Image.Resampling.LANCZOS)
        arr = np.array(img).astype(np.float32)
        rgb = arr[..., :3]
        alpha = arr[..., 3:4]
        lum = (0.299*rgb[...,0] + 0.587*rgb[...,1] + 0.114*rgb[...,2]) / 255.0
        tinted = lum[..., None] * target_rgb[None, None, :]
        out_rgb = np.clip(tinted, 0, 255).astype(np.uint8)
        out_arr = np.concatenate([out_rgb, alpha.astype(np.uint8)], axis=-1)
        out_img = Image.fromarray(out_arr, 'RGBA')
        out_img.save(temp_path)
        out_img.close()
        img.close()
    return temp_path


# Permission check on commands
def permission_check():
    async def predicate(interaction: discord.Interaction):
        user = interaction.guild.get_member(interaction.user.id)
        allowed_roles = server_settings(False, interaction.guild, "roles")
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
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open("output.txt", "a") as f:
        f.write(f"[{now}] {"[ERROR   ]" if error else "[INFO    ]"} {msg}\n")
    if error:
        return f"\033[31m[{now}] [ERROR   ] {msg}"
    else:
        return f"\033[92m[{now}] [INFO    ] {msg}"

# lowkirk forgot about this file
# uhh thing that wait what was i gonn add
# type checker for a specfiic command (/xpconfig)
def to_text(data: dict, xpconfig=False):
    msg = []
    for key, value in data.items():
        _type = type(value)
        skib = value
        if _type == int:
            if xpconfig:
                if not key == "channel":
                    if value:
                        skib = "On"
                    else:
                        skib = "Off"
                else:
                    if value == 1:
                        skib = "Current Channel"
                    else:
                        skib = f"<#{value}>"
            else:
                skib = f"<#{value}>"
        elif _type == list:
            if xpconfig:
                skib = f"{value[0]} to {value[1]}"
            else:
                skib = ""
                for val in value:
                    skib += f"<@&{val}>"
                msg.append(f"{kirk[key]} are {skib}")
                continue
        msg.append(f"{kirk[key]} is {skib}")
    return "\n".join(msg)

# Log to a file and close the bot
def close_bot():
    with open("output.txt", "a") as f:
        f.write(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] Bot session was ended.\n")
    requests.patch("https://discord.com/api/v10/channels/1403041372751265912", headers={"Authorization":"Bot " + os.getenv("TOKEN"), "Content-Type": "application/json"}, data=json.dumps({"name": "[ 🔴 ] | Bot Status: Offline"}))