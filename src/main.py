import os
import discord
from discord.ext import commands

import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

import cogs

bot = commands.Bot(command_prefix='-')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.add_cog(cogs.Emotes(bot))

bot.run(os.getenv('DISCORD_BOT_TOKEN'))