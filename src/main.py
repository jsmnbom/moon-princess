import db
import cogs
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from tortoise import Tortoise
import sys
import asyncio
import signal

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

load_dotenv()

sys.path.append('.')


class Help(discord.ext.commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = 'Other'


bot = commands.Bot(command_prefix='-', help_command=Help())


@bot.event
async def on_ready():
    logging.info('Logged in as %s (%s) ', bot.user.name, bot.user.id)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("-help"))

for cog in map(cogs.__dict__.get, cogs.__all__):
    bot.add_cog(cog(bot))


def _cancel_tasks(loop):
    try:
        task_retriever = asyncio.Task.all_tasks
    except AttributeError:
        task_retriever = asyncio.all_tasks

    tasks = {t for t in task_retriever(loop=loop) if not t.done()}

    if not tasks:
        return

    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(
        *tasks, loop=loop, return_exceptions=True))

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': task.exception(),
                'task': task
            })


def run():
    loop = asyncio.get_event_loop()

    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    except NotImplementedError:
        pass

    async def runner():
        try:
            await db.init()
            await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
        finally:
            await bot.close()
            await Tortoise.close_connections()

    def stop_loop_on_completion(f):
        loop.stop()

    future = asyncio.ensure_future(runner(), loop=loop)
    future.add_done_callback(stop_loop_on_completion)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        future.remove_done_callback(stop_loop_on_completion)
        try:
            _cancel_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            loop.close()

    if not future.cancelled():
        return future.result()


if __name__ == '__main__':
    run()
