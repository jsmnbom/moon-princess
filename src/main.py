import os
import discord
from discord.ext import commands

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

import cogs

class Help(discord.ext.commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = 'Other'

bot = commands.Bot(command_prefix='-', help_command=Help())

@bot.event
async def on_ready():
    logging.info('Logged in as %s (%s) ', bot.user.name, bot.user.id)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("-help"))

bot.add_cog(cogs.Emotes(bot))

bot.run(os.getenv('DISCORD_BOT_TOKEN'))