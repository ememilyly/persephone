from discord.ext import commands
import logging
import persephone

_log = logging.getLogger(__name__)


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = _log

    @commands.before_invoke(persephone.invokers.log_command)
    @commands.command(
        help="Prune previous chat messages in the current channel",
    )
    async def prune(
        self,
        ctx,
        num: str = commands.parameter(
            description="Number of messages to prune", default=None
        ),
    ):
        if num:
            if ctx.channel.permissions_for(ctx.author).manage_messages and num.isdigit():
                limit = 100
                if limit > int(num):
                    limit = num
                async for message in ctx.history(limit=int(num) + 1):
                    await message.delete()
        else:
            await ctx.message.add_reaction('❓')


async def setup(bot):
    _log.info(f"loading {__name__}")
    await bot.add_cog(moderation(bot))
