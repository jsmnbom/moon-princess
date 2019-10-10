import discord
from discord.ext import commands
import db
import re

WEBHOOK_NAME = 'Moon Princess Proxy'

class DadBot(commands.Cog, name='Options'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        match = re.match(r'''^(?:i'm|i am)\s(.*)''', message.content, re.MULTILINE | re.IGNORECASE)
        if match:
            db_options, _ = await db.GuildOptions.get_or_create(guild_id=message.guild.id)

            if message.channel.id in db_options.dadbot_enabled_channels:
                for webhook in await message.channel.webhooks():
                    if webhook.name == WEBHOOK_NAME:
                        await webhook.send(f'Hi {match.group(1)}, I\'m dad!', username='Dad', avatar_url='https://i.imgur.com/YaP098z.jpg')

    @commands.group()
    async def dadbot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid subcommand. See `{}help dadbot` for more info.'.format(await ctx.bot.get_prefix(ctx.message)))

    @dadbot.command(name='showenabled', aliases=['show'])
    async def show_enabled(self, ctx):
        db_options, _ = await db.GuildOptions.get_or_create(guild_id=ctx.guild.id)

        channels = ctx.guild.text_channels

        channels = [channel for channel in channels if channel.id in db_options.dadbot_enabled_channels]

        if not channels:
            await ctx.send('Dadbot not enabled for any channels.')
        else:
            await ctx.send('Dadbot enabled channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))

    @dadbot.command()
    async def enable(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        db_options, _ = await db.GuildOptions.get_or_create(guild_id=ctx.guild.id)

        if not channels:
            channels = ctx.guild.text_channels

        db_options.dadbot_enabled_channels = list(set(db_options.dadbot_enabled_channels) | set(channel.id for channel in channels))
        await db_options.save()

        for channel in channels:
            await channel.create_webhook(name=WEBHOOK_NAME)

        await ctx.send('Enabling dadbot for channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))

    @dadbot.command()
    async def disable(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        db_options, _ = await db.GuildOptions.get_or_create(guild_id=ctx.guild.id)

        if not channels:
            channels = ctx.guild.text_channels

        db_options.dadbot_enabled_channels = list(set(db_options.dadbot_enabled_channels) - set(channel.id for channel in channels))
        await db_options.save()

        for channel in channels:
            for webhook in await channel.webhooks():
                if webhook.name == WEBHOOK_NAME:
                    await webhook.delete()

        await ctx.send('Disabling dadbot for channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))