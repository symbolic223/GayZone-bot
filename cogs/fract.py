import disnake
from disnake.ext import commands
import sqlite3

conn = sqlite3.connect("Van.db")
cursor = conn.cursor()

cursor.execute('''
        CREATE TABLE IF NOT EXISTS fractions (
            name TEXT PRIMARY KEY,
            leader INTEGER NOT NULL,
            color TEXT
        )
''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
        member INTEGER PRIMARY KEY,
        frac TEXT
        )
''')
conn.commit()


class FractCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_ids = {}

    @commands.slash_command(name = "add-fraction", description = "Добавляет новую фракцию в базу данных")
    @commands.has_permissions(administrator = True)
    async def add_frac(self, inter, name, leader: disnake.Member, color: str):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        if frac:
            await inter.response.send_message("Фракция уже существует", ephemeral = True)
            return
        elif len(color) > 6:
            await inter.response.send_message("Вы ввели неправильный цвет", ephemeral = True)
            return
        else:
            cursor.execute("INSERT INTO fractions (name, leader, color) VALUES (?, ?, ?)", (name, leader.id, color))
            cursor.execute("INSERT INTO members (member, frac) VALUES (?, ?)", (leader.id, name))
            conn.commit()
            await inter.response.send_message(f"Фракция {name} успешно создана. Её лидер - {leader.mention}")

    @commands.slash_command(name="delete-fraction", description="Удаляет фракцию из базы данных")
    @commands.has_permissions(administrator=True)
    async def del_frac(self, inter, name):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        if not frac:
            await inter.response.send_message("Фракции не существует", ephemeral = True)
            return
        else:
            cursor.execute("DELETE FROM fractions WHERE name = ?", (name,))
            cursor.execute("DELETE FROM members WHERE frac = ?", (name,))
            conn.commit()
            await inter.response.send_message(f"Фракция {name} успешно удалена")

    @commands.slash_command(name="change-leader", description="Меняет лидера фракции")
    @commands.has_permissions(administrator=True)
    async def lead_change(self, inter, name, leader: disnake.Member):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        cursor.execute("SELECT leader FROM fractions WHERE name = ?", (name,))
        owner = cursor.fetchone()
        cursor.execute("SELECT * FROM members WHERE member = ?", (leader.id,))
        mem = cursor.fetchone()
        if not frac:
            await inter.response.send_message("Фракции не существует", ephemeral = True)
            return
        elif mem[1] != frac[0]:
            await inter.response.send_message("Участник уже находится во фракции", ephemeral = True)
            return
        elif owner[0] == leader.id:
            await inter.response.send_message(f"{leader.mention} и так лидер этой фракции", ephemeral = True)
        else:
            cursor.execute("UPDATE fractions SET leader = ? WHERE name = ?", (leader.id, name))
            conn.commit()
            await inter.response.send_message(f"Лидером фракции {name} успешно назначен {leader.mention}")

    @commands.slash_command(name = "add-member", description = "Добавляет участника во фракцию")
    async def add_member(self, inter, member: disnake.Member):
        cursor.execute("SELECT * FROM fractions WHERE leader = ?", (inter.author.id,))
        owner = cursor.fetchone()
        cursor.execute("SELECT name FROM fractions WHERE leader = ?", (inter.author.id,))
        owner_frac = cursor.fetchone()
        cursor.execute("SELECT * FROM members WHERE member = ?", (member.id,))
        mem = cursor.fetchone()

        if not owner:
            await inter.response.send_message("Вы не являетесь лидером фракции", ephemeral = True)
            return
        elif mem is not None:
            await inter.response.send_message("Участник уже находится во фракции", ephemeral = True)
            return
        else:
            cursor.execute("INSERT INTO members (member, frac) VALUES (?, ?)", (member.id, owner_frac[0]))
            conn.commit()
            await inter.response.send_message(f"Участник {member.mention} успешно добавлен во фракцию {owner_frac[0]}")

    @commands.slash_command(name="delete-member", description="Удаляет участника из фракции")
    async def del_member(self, inter, member: disnake.Member):
        cursor.execute("SELECT * FROM fractions WHERE leader = ?", (inter.author.id,))
        owner = cursor.fetchone()
        cursor.execute("SELECT name FROM fractions WHERE leader = ?", (inter.author.id,))
        owner_frac = cursor.fetchone()
        cursor.execute("SELECT * FROM members WHERE member = ?", (member.id,))
        mem = cursor.fetchone()
        if not owner:
            await inter.response.send_message("Вы не являетесь лидером фракции", ephemeral=True)
            return
        elif not mem:
            await inter.response.send_message("Участника нет в этой фракции", ephemeral = True)
            return
        else:
            cursor.execute("DELETE FROM members WHERE member = ?", (member.id,))
            conn.commit()
            await inter.response.send_message(f"Участник {member.mention} успешно исключен из фракции {owner_frac[0]}")

    @commands.slash_command(name = "leave", description = "Выйти из фракции")
    async def leave(self, inter):
        cursor.execute("SELECT * FROM members WHERE member = ?", (inter.author.id,))
        member = cursor.fetchone()
        cursor.execute("SELECT * FROM fractions WHERE leader = ?", (inter.author.id,))
        lead = cursor.fetchone()
        if lead:
            await inter.response.send_message("Вы являетесь лидером фракции. Для начала передайте лидера перед выходом", ephemeral = True)
            return
        elif not member:
            await inter.response.send_message("Вы и так не находитесь во фракции", ephemeral = True)
            return
        else:
            cursor.execute("DELETE FROM members WHERE member = ?", (inter.author.id,))
            conn.commit()
            await inter.response.send_message("Вы успешно покинули фракцию", ephemeral = True)


    @commands.slash_command(name="get-fractions", description="Возвращает список фракций и её лидеров")
    async def get_frac(self, inter):
        cursor.execute("SELECT * FROM fractions")
        fracs = cursor.fetchall()

        if not fracs:
            await inter.response.send_message("Фракции не найдены.", ephemeral=True)
            return

        embeds = []
        for frac in fracs:
            name, leader_id, color = frac
            leader = inter.guild.get_member(leader_id)
            leader_mention = leader.mention if leader else "Неизвестный лидер"

            cursor.execute("SELECT member FROM members WHERE frac = ?", (name,))
            members = cursor.fetchall()
            member_mentions = [inter.guild.get_member(member[0]).mention for member in members if
                               inter.guild.get_member(member[0])]

            if member_mentions:
                members_list = ", ".join(member_mentions)

            embed = disnake.Embed(
                title=f"Список участников фракции {name}",
                description=f"Лидер: {leader_mention}\nУчастники: {members_list}",
                color=int(color, 16)
            )
            embeds.append(embed)

        await inter.response.send_message(embeds=embeds)


def setup(bot: commands.Bot):
    bot.add_cog(FractCog(bot))