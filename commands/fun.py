import discord, random, asyncio
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.methods import log
from resources.variables import sp

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playlists", description="Pick any amount of random songs from any user of your choice playlist!")
    @app_commands.describe(user="User to pick", amount="How many random songs?")
    @app_commands.choices(user=[
            app_commands.Choice(name="Yuker", value="7z71MvgtNCMcHtkmn4uOZ2"),
            app_commands.Choice(name="AVeemo", value="2avOzDLDfrd79OgB94oTnK"),
            app_commands.Choice(name="Ryzen", value="04nIivJtm9XIRg4Gf3y3EX"),
            app_commands.Choice(name="JakeJ", value="2OTDsYmgloSEfcyV1eSJRQ", ),
            app_commands.Choice(name="YukerAndCo", value="3f0Qvrvp2GNcKBLt7nVGlp"),
            app_commands.Choice(name="Shell Lurker", value="3xuRhkqSjBKw2H1EZ0tsHL"),
            app_commands.Choice(name="Parish", value="02yzCvHEKF844OuRywdJ07"),
            app_commands.Choice(name="Macchiato", value="6rdMEEWVG8Gi0g25oybVtr")
        ])
    async def playlist(self, interaction: discord.Interaction, user: app_commands.Choice[str], amount: int):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        await interaction.response.defer()
        if amount < 1 or amount > 200:
            amount = 1
        await interaction.followup.send("\n".join(f"[__{t['track']['name']}__ by **{', '.join(artist['name'] for artist in t['track']['artists'])}**](https://open.spotify.com/track/{t['track']['id']})"for t in random.sample(sp.playlist_tracks(user.value)["items"], amount)))

    @app_commands.command(name="discography", description="Get a random song from a band's Spotify discography.")
    @app_commands.describe(artist="Enter any artist's name")
    async def discography(self, interaction: discord.Interaction, artist: str):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        await interaction.response.defer()
        results = sp.search(q=artist, type='artist')

        if not results['artists']['items']:
            await interaction.followup.send(f'Failed to find Artist "{artist}" on Spotify.')
            return

        artist_id = results['artists']['items'][0]['id']

        albums = []
        results = sp.artist_albums(artist_id, album_type='album')
        albums.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

        all_tracks = []
        for album in albums:
            album_id = album['id']
            tracks = sp.album_tracks(album_id)['items']
            all_tracks.extend(tracks)

        if not all_tracks:
            await interaction.followup.send(f'No tracks found from "{artist}"\'s discography')
            return

        track = random.choice(all_tracks)
        await interaction.followup.send(f"__**Random song from {artist}**__:\n[**{track['name']}**]({track['external_urls']['spotify']})")

    @app_commands.command(name="silly", description="Get your silliness percentage")
    @app_commands.describe(user="Enter a user")
    async def silly(self, interaction: discord.Interaction, user: discord.Member = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        dynevil = ""
        if user == None:
            user = interaction.user

        rand = random.randint(0, 115)
        if rand > 100:
            danr = rand - 100
            rand = rand - danr

        if rand == 100:
            dynevil = "__**PURE SILLY!!**__"
        elif rand >= 75:
            dynevil = "**SILLY!!**"
        elif rand >= 50:
            dynevil = "SILLY!"
        elif rand >= 25:
            dynevil = "silly!"
        else:
            dynevil = "silly."

        evil = discord.Embed(title="Silly Calculator",
                             description=f"This **SILLY** calculator will determine your silliness, {user.mention}...",
                             color=discord.Color.yellow())
        await interaction.response.send_message(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name=".", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". . .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name="", value=f"{user.mention} is {rand}% {dynevil}")
        await interaction.edit_original_response(embed=evil)

    @app_commands.command(name="evil", description="Get your evilness percentage")
    @app_commands.describe(user="Enter a user")
    async def evil(self, interaction: discord.Interaction, user: discord.Member = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        dynevil = ""
        if user == None:
            user = interaction.user

        rand = random.randint(0, 115)

        if rand >= 100:
            rand = 100
            dynevil = "__**PURE EVIL!!**__"
        elif rand >= 75:
            dynevil = "**EVIL!!**"
        elif rand >= 50:
            dynevil = "EVIL!"
        elif rand >= 25:
            dynevil = "evil!"
        else:
            dynevil = "evil."

        evil = discord.Embed(title="Evil Calculator",
                             description=f"This **EVIL** calculator will determine your silliness, {user.mention}...",
                             color=discord.Color.yellow())
        await interaction.response.send_message(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name=".", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". . .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name="", value=f"{user.mention} is {rand}% {dynevil}")
        await interaction.edit_original_response(embed=evil)

async def setup(bot):
    await bot.add_cog(Fun(bot))
