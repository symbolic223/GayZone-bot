import disnake
from disnake.ext import commands

class ModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        mes_u = disnake.Embed(
            title = f"Жалоба на игрока от {message.author.name}",
            description="В этой ветке действуют все правила, просьба их соблюдать.",
            color = 0x2084fc
        )
        mes_a = disnake.Embed(
            title=f"Жалоба на администратора от {message.author.name}",
            description="В этой ветке действуют все правила, просьба их соблюдать.",
            color=0x2084fc
        )
        user_c = await self.bot.fetch_channel(1221459197288513617)
        adm_c = await self.bot.fetch_channel(1221459172122693632)

        if message.channel == user_c:
            th = await message.create_thread(name = f"Жалоба от {message.author.name}", auto_archive_duration=None)
            await th.send(embed = mes_u)
        if message.channel == adm_c:
            th = await message.create_thread(name = f"Жалоба от {message.author.name}", auto_archive_duration=None)
            await th.send(embed = mes_a)



def setup(bot: commands.Bot):
    bot.add_cog(ModCog(bot))