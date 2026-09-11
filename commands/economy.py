import discord, random
from datetime import datetime, timedelta
from discord import app_commands
from discord.ext import commands
from resources.enums import Economy, GambleGames
from resources.variables import noMentions
from Cogs.database import economy as ecoCmd
from Cogs.Methods.methods import logCommand

dailyReward = 100
lost = .95
otherLost = .05
gain = [60, 100]
claimCD = timedelta(days=1)

games = []
for g in GambleGames:
    games.append(app_commands.Choice(name=g.name, value=str(g.value)))

slotSymbols = ["🍒", "🍋", "🍊", "⭐", "💎"]

class Eco(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="eco", description="Economy commands")
        self.bot = bot

    @app_commands.command(name="daily", description="Claim your daily reward!")
    @app_commands.allowed_contexts(True, True, True)
    async def daily(self, interaction: discord.Interaction):
        print(logCommand(interaction))
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        data = ecoCmd(Economy.Get, None, user)
        money, dailytime = data.values()
        timeDiff = datetime.now() - dailytime
        if timeDiff >= claimCD:
            ecoCmd(Economy.Set,{
                    "money": money + dailyReward,
                    "dailytime": int(datetime.now().timestamp())
                }, user
            )
            await interaction.followup.send(f"Successfully claimed ${dailyReward} as a daily reward!")
        else:
            hours, remainder = divmod(int((claimCD - timeDiff).total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.followup.send(f"Please wait {hours}h {minutes}m {seconds}s before claiming your daily reward again!")

    @app_commands.command(name="throw", description="Throw money at someone!")
    @app_commands.describe(user="The user to throw money at", amount="Amount of money to throw")
    @app_commands.allowed_contexts(True, True, True)
    async def throw(self, interaction: discord.Interaction, user: discord.User, amount: float):
        print(logCommand(interaction))
        await interaction.response.defer()
        if user.bot:
            await interaction.followup.send(f"You cannot throw money at a {user.mention}, they're a bot!", allowed_mentions=noMentions)
            return
        if user == interaction.user:
            await interaction.followup.send("You cannot throw money at yourself!", allowed_mentions=noMentions)
            return

        data = ecoCmd(Economy.Get, None, interaction.user)
        money: int = data["money"]
        if amount > money:
            await interaction.followup.send(f"You do not have enough money (${amount:.2f}) to throw at {user.name}!", allowed_mentions=noMentions)
            return
        if amount <= 0:
            await interaction.followup.send(f"${amount:.2f} is an invalid amount! Pick a number above 0.")

        data2 = ecoCmd(Economy.Get, None, user)
        otherMoney: int = data2["money"]

        percent = random.randint(gain[0], gain[1])
        ylost = amount * lost
        tlost = min(otherMoney * otherLost, 500)
        tGot  = amount * (percent / 100)

        ecoCmd(Economy.Take, ylost, interaction.user)
        ecoCmd(Economy.Take, tlost, user)
        ecoCmd(Economy.Add,  tGot,  user)

        await interaction.followup.send(f"You lost ${ylost:.2f} and {user.mention} lost ${tlost:.2f} but gained ${tGot:.2f} ({percent}%)!", allowed_mentions=noMentions)
        if interaction.guild is None:
            if isinstance(interaction.channel, discord.DMChannel):
                if interaction.channel.recipient != user:
                    await user.send(f"{interaction.user.mention} ({interaction.user.name}) made you lose ${tlost:.2f}, but you gained ${tGot:.2f} from their thrown money!")

    @app_commands.command(name="donate", description="Donate money to someone!")
    @app_commands.describe(user="The user to donate money to", amount="Amount of money to donate")
    @app_commands.allowed_contexts(True, True, True)
    async def donate(self, interaction: discord.Interaction, user: discord.User, amount: float):
        print(logCommand(interaction))
        await interaction.response.defer()
        if user.bot:
            await interaction.followup.send(f"You cannot donate money to a {user.mention}, they're a bot!", allowed_mentions=noMentions)
            return
        if user == interaction.user:
            await interaction.followup.send("You cannot donate money to yourself!", allowed_mentions=noMentions)
            return

        data = ecoCmd(Economy.Get, None, interaction.user)
        money: int = data["money"]

        if amount > money:
            await interaction.followup.send(f"You do not have enough money (${amount:.2f}) to donate to {user.name}!", allowed_mentions=noMentions)
            return
        if amount <= 0:
            await interaction.followup.send(f"${amount:.2f} is an invalid amount! Pick a number above 0.")

        ecoCmd(Economy.Take, amount, interaction.user)
        ecoCmd(Economy.Add , amount, user)

        await interaction.followup.send(f"Successfully donated ${amount:.2f} to {user.mention}!", allowed_mentions=noMentions)
        if interaction.guild is None:
            if isinstance(interaction.channel, discord.DMChannel):
                if interaction.channel.recipient != user:
                    await user.send(f"{interaction.user.mention} ({interaction.user.name}) donated ${amount:.2f} to you!")

    @app_commands.command(name="gamble", description="Gamble your money, getting or losing money is up to luck...")
    @app_commands.describe(game="The game to gamble on", bet="The amount of money you're betting", value="Value for the game if applicable")
    @app_commands.choices(game=games)
    @app_commands.allowed_contexts(True, True, True)
    async def gamble(self, interaction: discord.Interaction, game: app_commands.Choice[str], bet: float, value: str | None = None):
        print(logCommand(interaction))
        await interaction.response.defer()

        data = ecoCmd(Economy.Get, None, interaction.user)
        money: int = data["money"]

        if bet > money or bet <= 0:
            await interaction.followup.send("Invalid bet amount.")
            return

        won = False
        wonAmount = bet
        rslt = ""
        if value: value = value.strip().lower();

        match GambleGames(int(game.value)):
            case GambleGames.Slots:
                spin = [random.choice(slotSymbols) for _ in range(3)]

                won = spin[0] == spin[1] == spin[2]
                wonAmount = bet * 5
                rslt = ' | '.join(spin)
            case GambleGames.Roulette:
                if value not in ["red", "black"]:
                    await interaction.followup.send('Please choose "Red" or "Black" as your value option!')
                    return
                outcome = random.choice(["red", "black", "green"])
                won = value == outcome
                if outcome == "green": wonAmount = bet * 10
                rslt = f"Ball landed on **{outcome}**"
            case GambleGames.Coinflip:
                if value not in ["heads", "tails"]:
                    await interaction.followup.send('Please choose "Heads" or "Tails" as your value option!')
                    return
                flip = random.choice(["heads", "tails"])
                won = value == flip
                wonAmount = bet
                rslt = f"Coin landed on **{flip}**"
            case GambleGames.HighLow:
                success = False
                try:
                    value = int(value)
                    if not (value < 1 or value > 100): success = True;
                except: pass;

                if not success:
                    await interaction.followup.send('Please enter a valid number between "1" and "100" as your guess.')
                    return

                roll = random.randint(1, 100)
                won = value == roll
                wonAmount = bet * 10
                rslt = f"You guessed **{value}**. The number was **{roll}**."
            case GambleGames.Blackjack:
                player = random.randint(13, 23)
                dealer = random.randint(13, 23)
                won = (player <= 21 and (player > dealer or dealer > 21))
                rslt = f"You drew **{player}**, Dealer drew **{dealer}**."
            case GambleGames.DiceRoll:
                if value not in ["high", "low"]:
                    await interaction.followup.send('Please choose "High" or "Low" as your value option!')
                    return

                roll = random.randint(1, 6)
                won = (value == "high" and roll >= 4) or (value == "low" and roll <= 3)
                rslt = f"You guessed **{value.capitalize()}**. The die rolled **{roll}**."
            case GambleGames.GuessNumber:
                success = False
                try:
                    value = int(value)
                    if not (value < 1 or value > 10): success = True;
                except: pass;

                if not success:
                    await interaction.followup.send('Please enter a valid number between "1" and "10" as your guess.')
                    return

                number = random.randint(1, 10)
                won = (value == number)
                wonAmount = bet * 8
                rslt = f"You guessed **{value}**. The secret number was **{number}**."

        ecoCmd(Economy.Get if won else Economy.Take, wonAmount if won else bet, interaction.user)
        await interaction.followup.send(rslt + "\n" + (f"You won ${wonAmount:.2f}!" if won else f"You lost ${bet:.2f}!"))

    @app_commands.command(name="balance", description="Check your balance!")
    @app_commands.allowed_contexts(True, True, True)
    async def balance(self, interaction: discord.Interaction):
        print(logCommand(interaction))
        await interaction.response.defer()

        data = ecoCmd(Economy.Get, None, interaction.user)
        money: int = data["money"]

        await interaction.followup.send(f"You have 🪙 ${money:.2f}.")

async def setup(bot: commands.Bot):
    bot.tree.add_command(Eco(bot))
