import sys

class AudioopStub:
    """Stub module pour remplacer audioop dans Python 3.13+"""
    def __getattr__(self, name):
        raise AttributeError(f"audioop.{name} n'est pas disponible")

sys.modules['audioop'] = AudioopStub()

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERREUR: DISCORD_TOKEN n'est pas défini dans le fichier .env")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connecté: {bot.user.name}')
    await bot.change_presence(
        activity=discord.CustomActivity(name="🪦"),
        status=discord.Status.idle
    )

bot.run(TOKEN)
