import disnake
from disnake.ext import commands
import sqlite3

conn = sqlite3.connect("Van.db")
cursor = conn.cursor()

cursor.execute('''
        CREATE TABLE IF NOT EXISTS fractions (
            name TEXT PRIMARY KEY,
            leader INTEGER NOT NULL
        )
''')
conn.commit()


class FractCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name = "add-fraction", description = "Добавляет новую фракцию в базу данных")
    @commands.has_permissions(administrator = True)
    async def add_frac(self, inter, name, leader: disnake.Member):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        if frac:
            await inter.response.send_message("Фракция уже существует")
            return
        else:
            cursor.execute("INSERT INTO fractions (name, leader) VALUES (?, ?)", (name, leader.id))
            conn.commit()
            await inter.response.send_message(f"Фракция {name} успешно создана. Её лидер - {leader.mention}")

    @commands.slash_command(name="delete-fraction", description="Удаляет фракцию из базы данных")
    @commands.has_permissions(administrator=True)
    async def del_frac(self, inter, name):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        if not frac:
            await inter.response.send_message("Фракции не существует")
            return
        else:
            cursor.execute("DELETE FROM fractions WHERE name = ?", (name,))
            conn.commit()
            await inter.response.send_message(f"Фракция {name} успешно удалена")

    @commands.slash_command(name="change-leader", description="Меняет лидера фракции")
    @commands.has_permissions(administrator=True)
    async def lead_change(self, inter, name, leader: disnake.Member):
        cursor.execute("SELECT * FROM fractions WHERE name = ?", (name,))
        frac = cursor.fetchone()
        cursor.execute("SELECT leader FROM fractions WHERE name = ?", (name,))
        owner = cursor.fetchone()
        if not frac:
            await inter.response.send_message("Фракции не существует")
            return
        elif owner[0] == leader.id:
            await inter.response.send_message(f"{leader.mention} и так лидер этой фракции")
        else:
            cursor.execute("UPDATE fractions SET leader = ? WHERE name = ?", (leader.id, name))
            conn.commit()
            await inter.response.send_message(f"Лидером фракции {name} успешно назначен {leader.mention}")

def setup(bot: commands.Bot):
    bot.add_cog(FractCog(bot))