import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

UPDATE_CHANNEL_ID = 1500691578916962344

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

COLORS = {
    "stable": 0x2ecc71,
    "update": 0x3498db,
    "beta":   0xf1c40f,
    "hotfix": 0xe74c3c
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx, tipo: str, version: str, version_anterior: str, cambios: str, link_apk: str, link_repo: str):
    
    channel = bot.get_channel(UPDATE_CHANNEL_ID)
    
    if channel is None:
        await ctx.send("❌ No encontré el canal de anuncios.")
        return

    color = COLORS.get(tipo.lower(), 0x3498db)
    fecha = datetime.now().strftime("%d/%m/%y")

    embed = discord.Embed(
        description=(
            f"# 🚀 NUEVA ACTUALIZACIÓN DISPONIBLE\n"
            f"### DarkSong {version}\n\n"
            f"### 📅 {fecha}\n\n"
            f"## ✨ Novedades\n"
            f"{cambios}\n\n"
            f"## ⬆️ Nueva versión: {version}\n"
            f"## 📦 Versión anterior: {version_anterior}"
        ),
        color=color
    )
    embed.set_footer(text="DarkSong Updater • Powered by GitHub Releases")

    row = discord.ui.View()
    row.add_item(discord.ui.Button(
        label="📥 Descargar APK",
        style=discord.ButtonStyle.success,
        url=link_apk
    ))
    row.add_item(discord.ui.Button(
        label="🌐 Repositorio de GitHub",
        style=discord.ButtonStyle.link,
        url=link_repo
    ))

    await channel.send(f"<@&1496312737721090278>", embed=embed, view=row)
    await ctx.message.delete()

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Uso correcto: `!update [tipo] [versión] [versión_anterior] \"Cambios\" [link_apk] [link_repo]`\n**Tipos:** stable, update, beta, hotfix")

bot.run(TOKEN)
