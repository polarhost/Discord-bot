import nextcord
from nextcord.ext import commands
import os
from keep_alive import keep_alive
keep_alive()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', help_command=None, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is running")

@bot.slash_command(description="Just a test command.")
async def test(interaction: nextcord.Interaction):
    em = nextcord.Embed(
        title="Test Bot",
        description="Testing!",
        color=nextcord.Color.blue
    )
    await interaction.response.send_message(embed=em)

bot.run(os.environ['TOKEN'])
