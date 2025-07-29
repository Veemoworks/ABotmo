from imports import *

load_dotenv()
bot = commands.Bot(command_prefix=";;", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        cogs = [ "commands.fun" ]
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
    except Exception as e:
        print(f"Error occurred in starting up the bot!: {e}")

@bot.event
async def on_command_error(ctx, error):
    print(f"Fatal error occurred: {error}")
    try:
        embed = discord.Embed(title="BOT STATUS!", colour=discord.Colour.purple())
        embed.add_field(name="Bot has encountered an error!", value=str(error)[:1024])
        embed.set_thumbnail(url=warm)
        embed.timestamp = datetime.now()

        channel = await bot.fetch_channel(1399721716606963843)
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send error message: {e}")
    errorembed = discord.Embed(title="Bot Error!", description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1396646022314328106>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!", color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
    errorembed.add_field(name="Exception:", value=error)
    await ctx.reply(embed=errorembed, mention_author=False)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"Fatal error occurred: {error}")
    try:
        embed = discord.Embed(title="BOT ERROR!", description=str(error)[:1024], colour=discord.Colour.purple())
        embed.set_thumbnail(url=warm)
        embed.timestamp = datetime.now()

        channel = await bot.fetch_channel(1399721716606963843)
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send error message: {e}")
    errorembed = discord.Embed(title="Bot Error!", description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1396646022314328106>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!", color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
    errorembed.add_field(name="Exception:", value=error)
    try:
        await interaction.response.send_message(embed=errorembed)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=errorembed)

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))