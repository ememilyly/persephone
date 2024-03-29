from discord.ext import commands
import logging
import persephone

from google_images_search import GoogleImagesSearch

_log = logging.getLogger(__name__)


class google(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = _log

    @commands.command(aliases=("img",), help="Find the first image on google")
    async def image(
        self,
        ctx,
        *,
        term: str = commands.parameter(description="What you want to look up"),
    ):
        if term:
            key = persephone.Secrets.get("GOOGLE_API_KEY")
            cx = persephone.Secrets.get("GOOGLE_ENGINE_ID")
            search = {
                "q": term,
                "num": 1,
                "safe": "off",
            }

            async with ctx.typing():
                gis = GoogleImagesSearch(key, cx)
                gis.search(search_params=search)

            await ctx.reply(gis.results()[0]._url)


async def setup(bot):
    _log.info(f"loading {__name__}")
    if persephone.Secrets.get("GOOGLE_API_KEY") and persephone.Secrets.get(
        "GOOGLE_ENGINE_ID"
    ):
        await bot.add_cog(google(bot))
    else:
        e = "no google api config found, not loading"
        _log.warning(e)
        raise commands.ExtensionError(e, name=__name__)
