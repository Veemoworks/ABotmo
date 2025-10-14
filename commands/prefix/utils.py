import discord, re
from datetime import datetime, timezone
from discord.ext import commands
from Cogs.Methods.methods import log
from Cogs.Methods.asynchronous.methods import logChannel

class UtilsPREFIX(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(name="purge", description="Deletes a number of messages with optional filters.")
    async def purge_prefix(self, ctx, amount: int, *filters):
        print(log(False,f"{ctx.author} ({ctx.author.id}) used {ctx.command.qualified_name} in {ctx.guild.id} ({ctx.guild.name})!"))

        if amount < 1 or amount > 100:
            msg = await ctx.send("Please provide a number between 1 and 100.")
            await msg.delete(delay=5)
            return

        user = None
        bots = False
        embeds = False
        files = False
        links = False
        mentions = False

        for f in filters:
            f = f.lower()
            if f.startswith("<@") and f.endswith(">"):
                user_id = int(re.sub(r"[<@!>]", "", f))
                user = ctx.guild.get_member(user_id)
            elif f == "bots":
                bots = True
            elif f == "embeds":
                embeds = True
            elif f == "files":
                files = True
            elif f == "links":
                links = True
            elif f == "mentions":
                mentions = True

        def check(msg: discord.Message):
            if user and msg.author != user:
                return False
            if bots and not msg.author.bot:
                return False
            if embeds and not msg.embeds:
                return False
            if files and not msg.attachments:
                return False
            if links and not re.search(r"https?://", msg.content):
                return False
            if mentions and not (msg.mentions or msg.role_mentions):
                return False
            return True

        try:
            deleted = await ctx.channel.purge(limit=amount + 1, check=check)
            if not deleted or len(deleted) <= 1:
                msg = await ctx.send("No messages matched your filters.")
                await msg.delete(delay=5)
                return

            count = len(deleted) - 1
            summary = f"Purged **{count}** messages."
            filters_used = []
            if user: filters_used.append(f"user: {user.display_name}")
            if bots: filters_used.append("bots")
            if embeds: filters_used.append("embeds")
            if files: filters_used.append("files")
            if links: filters_used.append("links")
            if mentions: filters_used.append("mentions")

            if filters_used:
                summary += f" *(filters: {', '.join(filters_used)})*"

            data = (ctx.author.id, ctx.author.id, amount, ctx.channel.mention, "PURGE", datetime.now().astimezone(timezone.utc).strftime("[%d|%m|%y] : [%H:%M]"))
            await logChannel(self.bot, ctx, data, ctx.channel)

            msg = await ctx.send(summary)
            await msg.delete(delay=5)

        except Exception as e:
            msg = await ctx.send(f"Could not purge messages: {e}")
            await msg.delete(delay=10)
            print(log(True, f"Error in purge command: {e}"))

async def setup(bot):
    await bot.add_cog(UtilsPREFIX(bot))