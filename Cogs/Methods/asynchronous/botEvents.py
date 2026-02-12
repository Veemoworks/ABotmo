import discord, time
from DataBases.database import xp, user_settings, xp_settings, xp_roles
from resources.links import warm
from Cogs.Methods.asynchronous.methods import crash, get_prefix
from Cogs.Methods.methods import log

# All bot related events

errorembed = discord.Embed(title="Bot Error!",
                           description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </stats:1441449914352533664>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!",
                           color=discord.Color.dark_green())
errorembed.set_thumbnail(url=warm)

# Prefix command error
async def command_error(ctx, error):
    await crash(error)
    errorembed.add_field(name="Exception:", value=str(error))
    await ctx.reply(embed=errorembed, mention_author=False)

# App command error
async def app_command_error(interaction: discord.Interaction, error):
    if str(error).startswith("The check functions for command "):
        return
    await crash(error)
    errorembed.add_field(name="Exception:", value=str(error))
    try:
        await interaction.response.send_message(embed=errorembed)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=errorembed)

async def message(msg: discord.Message):
    if msg.author.bot:
        return

    guild = msg.guild
    user = msg.author
    if guild:
        if msg.content.startswith(await get_prefix(None, msg)):
            return
        data = xp_settings(False, guild, None)
        if data["xpenabled"]:
            lvl_up, lvl = xp(True, guild, int(time.time()), user)

            if lvl_up:
                role = xp_roles(False, guild, lvl)
                try:
                    if not role is None:
                        role = guild.get_role(int(role))
                        if not role is None:
                            await user.add_roles(role, reason=f"Level up to {lvl}")
                    if data["messagetoggle"]:
                        if data["channel"] == 1:
                            await msg.reply(
                                f"{msg.author.mention}, you have succesfully leveled up to Level {lvl}!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False))
                        else:
                            await msg.guild.get_channel(data["channel"]).send(f"{msg.author.mention} has successfully leveled up to Level {lvl}")
                    else:
                        enabled = user_settings(False, user.id, "xpmessage")
                        if enabled:
                            if enabled == 2:
                                await user.send(f"{msg.author.mention}, you have succesfully leveled up to Level {lvl} in {guild.name} ({guild.id})!{"\n-# *You can toggle this message with /settings!*" if lvl % 5 == 0 else ""}")
                            else:
                               await msg.reply(f"{msg.author.mention}, you have succesfully leveled up to Level {lvl}!{"\n-# *You can toggle this message with /settings!*" if lvl % 5 == 0 else ""}", allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False))
                except Exception as e:
                    print(log(True, f"on_message raised an error: "+ str(e)))
                    pass