from discord.ext import commands
import logging
from configparser import ConfigParser
from udpy import UrbanClient
from google_images_search import GoogleImagesSearch

_log = logging.getLogger(__name__)

class stuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('ud',))
    async def urbandict(self, ctx, *args):
        if args:
            word = ' '.join(args)
            client = UrbanClient()
            defs = client.get_definition(word)
            if defs:
                m = defs[0].definition + '\ne.g.: ' + defs[0].example
                await ctx.send(m.replace('[','').replace(']',''))
            else:
                await ctx.send(f'No definition found for {word}')

async def setup(bot):
    await bot.add_cog(stuff(bot))
