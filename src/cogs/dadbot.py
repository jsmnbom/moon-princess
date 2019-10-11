import discord
from discord.ext import commands
import db
import re


class DadBot(commands.Cog, name='Options'):
    def __init__(self, bot):
        self.bot = bot

    @property
    def webhook_name(self):
        return f'{self.bot.user.name} Proxy'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        match = re.match(r'''^(?:i'm|i am|im)\s(.*)''',
                         message.content, re.MULTILINE | re.IGNORECASE)
        if match:
            ctx = await self.bot.get_context(message)
            guild_options = await ctx.get_guild_options()

            if message.channel.id in guild_options.dadbot_enabled_channels:
                for webhook in await message.channel.webhooks():
                    if webhook.name == self.webhook_name:
                        await webhook.send(f'Hi {match.group(1)}, I\'m dad!',
                                           username='Dad', avatar_url='https://i.imgur.com/YaP098z.jpg')

    @commands.group()
    async def dadbot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid subcommand. See `{}help dadbot` for more info.'
                           .format(await ctx.bot.get_prefix(ctx.message)))

    @dadbot.command(name='showenabled', aliases=['show'])
    async def show_enabled(self, ctx):
        guild_options = await ctx.get_guild_options()

        channels = ctx.guild.text_channels

        channels = [
            channel for channel in channels if channel.id in guild_options.dadbot_enabled_channels]

        if not channels:
            await ctx.send('Dadbot not enabled for any channels.')
        else:
            await ctx.send('Dadbot enabled channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))

    @dadbot.command()
    async def enable(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        guild_options = await ctx.get_guild_options()

        if not channels:
            channels = ctx.guild.text_channels

        guild_options.dadbot_enabled_channels = list(set(guild_options.dadbot_enabled_channels) |
                                                     set(channel.id for channel in channels))
        await guild_options.save()

        for channel in channels:
            await channel.create_webhook(name=self.webhook_name)

        await ctx.send('Enabling dadbot for channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))

    @dadbot.command()
    async def disable(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        guild_options = await ctx.get_guild_options()

        if not channels:
            channels = ctx.guild.text_channels

        guild_options.dadbot_enabled_channels = list(set(guild_options.dadbot_enabled_channels) -
                                                     set(channel.id for channel in channels))
        await guild_options.save()

        for channel in channels:
            for webhook in await channel.webhooks():
                if webhook.name == self.webhook_name:
                    await webhook.delete()

        await ctx.send('Disabling dadbot for channel(s): {}'.format(', '.join(channel.mention for channel in set(channels))))
