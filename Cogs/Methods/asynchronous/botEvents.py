import discord
from resources import discordElements
from Cogs.Methods.asynchronous.methods import crash

async def on_command_error(ctx, error):
    await crash(error)
    errorembed = discordElements.DiscordEmbeds.errorembed
    errorembed.add_field(name="Exception:", value=str(error))
    await ctx.reply(embed=errorembed, mention_author=False)


async def on_app_command_error(bot, interaction: discord.Interaction, error):
    await crash(error)
    errorembed = discordElements.DiscordEmbeds.errorembed
    errorembed.add_field(name="Exception:", value=str(error))
    try:
        await interaction.response.send_message(embed=errorembed)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=errorembed)