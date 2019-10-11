import db
import cogs
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import asyncio

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

load_dotenv()


class MoonPrincessBot(commands.Bot):
    class Help(discord.ext.commands.DefaultHelpCommand):
        def __init__(self):
            super().__init__()
            self.no_category = 'Other'

    def __init__(self):
        super().__init__(command_prefix='-', help_command=self.Help())

        self.loop.create_task(self.db_task())

        for cog in map(cogs.__dict__.get, cogs.__all__):
            self.add_cog(cog(self))

    async def on_ready(self):
        logging.info('Logged in as %s (%s) ', self.user.name, bot.user.id)
        await self.change_presence(status=discord.Status.online, activity=discord.Game("-help"))

    async def db_task(self):
        try:
            await db.init()
            while not self.is_closed():
                await asyncio.sleep(60)
        finally:
            await db.close()


if __name__ == '__main__':
    bot = MoonPrincessBot()
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
