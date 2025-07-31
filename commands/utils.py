import discord, psutil, requests, time, ping3
from discord import app_commands
from discord.ext import commands
from resources.dictionaries import hosts, script_urls
from resources.links import avatar
from Cogs.Methods.methods import log
from ping3 import ping

ping3.EXCEPTIONS = True

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Check the statuses of many services")
    async def status(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        await interaction.response.defer()
        msg = ""
        amount = 1
        thingy = {
            "CPU": f"{psutil.cpu_percent()}%",
            "RAM": f"{psutil.virtual_memory().percent}%",
            "Disk": f"{psutil.disk_usage('/').percent}%",
            "Battery": f"{int(psutil.sensors_battery().percent)}%" if psutil.sensors_battery() else "N/A",
            "Uptime": f"{int((time.time() - psutil.boot_time()) // 3600)}h {int(((time.time() - psutil.boot_time()) % 3600) // 60)}m",
        }

        try:
            msg += "### Main Server:\n"
            start = time.perf_counter()
            r = requests.get("http://127.0.0.0:8000/health")
            r.raise_for_status()
            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000
            msg += f"✅ {elapsed_ms:.2f}ms\n"
            amount += 1
            msg += "\n**__Stats__**:\n"
            for name, details in thingy.items():
                msg += f"{name}: {details}\n"
        except Exception as ex:
            msg += f"❌ Error: {ex}\n"

        msg += "### Website:\n"
        for name, host in hosts.items():
            try:
                delay = ping(host, timeout=10, unit="ms")
                if delay is None:
                    msg += f"❌ `{name}` No response\n"
                else:
                    msg += f"✅ `{name}` ({int(delay)} ms)\n"
                    amount += 1
            except ping3.errors.Timeout:
                msg += f"❌ `{name}` Timed Out\n"
            except Exception as ex:
                msg += f"❌ `{name}` Error: {ex}\n"

        msg += f"### Python Scripts:\n✅ `ABotmo` ({round(self.bot.latency * 1000)}ms)\n"

        for name, url in script_urls.items():
            url = f"http://127.0.0.1:{url}/health"
            try:
                start = time.perf_counter()
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                end = time.perf_counter()
                elapsed_ms = (end - start) * 1000
                msg += f"✅ `{name}` ({int(elapsed_ms)} ms)\n"
                amount += 1
            except Exception as ex:
                msg += f"❌ `{name}` Error: {ex}\n"

        msg += "❌ `Channel Topic Updater` Shutdown\n❌ `Minecraft Console Link` Shutdown\n"

        embed = discord.Embed(
            title="Server Status",
            description=f"{amount}/{len(hosts) + len(script_urls) + 4} services up and running!\n{msg}",
            color=discord.Color.brand_green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        embed = discord.Embed(title="Bot is online!", description=f"Latency is {round(self.bot.latency * 1000)}ms!", color=discord.Color.brand_green())
        embed.set_thumbnail(url=avatar)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))