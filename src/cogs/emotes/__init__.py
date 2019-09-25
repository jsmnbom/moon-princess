import discord
from discord.ext import commands
from random import Random
import json
import os.path
import aiohttp
import os

TENOR_API_KEY = os.getenv('TENOR_API_KEY')

def comma_separator(sequence):
    if not sequence:
        return ''
    if len(sequence) == 1:
        return sequence[0]
    return '{} and {}'.format(', '.join(sequence[:-1]), sequence[-1])

class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rng = Random()

        dir_path = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(dir_path, 'data.json'), 'r') as f:
            self.data = json.load(f)

    async def get_gif_url(self, gif_id):
        params = {
            'ids': gif_id,
            'key': TENOR_API_KEY,
            'media_filter': 'minimal'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.tenor.com/v1/gifs', params=params) as r:
                print(r.url)
                if r.status == 200:
                    data = await r.json()
                    return data['results'][0]['media'][0]['gif']['url']
                else:
                    print('WTF')

    @commands.command()
    async def hug(self, ctx, members: commands.Greedy[discord.Member]):
        if len(members) == 0 or (len(members) == 1 and members[0] == ctx.author):
            text = f'{ctx.author.mention}, you look like you could use a hug.'
            gif_choices = self.data['hugs']
        elif len(members) == 1:
            if members[0] == ctx.bot.user:
                text = f'Nice try, {ctx.author.mention}'
                gif_choices = self.data['failed_hugs']
            else:
                text = f'{members[0].mention} you got hugged by {ctx.author.mention}.'
                gif_choices = self.data['hugs']
        else:
            text = f'{comma_separator([member.mention for member in members])} you got hugged by {ctx.author.mention}.'
            gif_choices = self.data['group_hugs']
        embed = discord.Embed(description=text)

        gif_id = self.rng.choice(gif_choices)
        gif_url = await self.get_gif_url(gif_id)
        embed.set_image(url=gif_url)

        await ctx.send(embed=embed)
