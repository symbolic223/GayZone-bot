import jishaku
from disnake.ext import commands
from jishaku.cog import Jishaku


class CustomDebugCog(Jishaku):
    pass


def setup(bot: commands.Bot):
    jishaku.Flags.NO_UNDERSCORE = True
    jishaku.Flags.NO_DM_TRACEBACK = True
    jishaku.Flags.FORCE_PAGINATOR = True
    bot.add_cog(CustomDebugCog(bot=bot))