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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx, version: str, cambios: str, link: str):
    
    channel = bot.get_channel(UPDATE_CHANNEL_ID)
    
    if channel is None:
        await ctx.send("❌ No encontré el canal de anuncios.")
        return

    fecha = datetime.now().strftime("%d/%m/%y")

    await channel.send(
        f"### :calendar: {fecha}\n"
        f"## <:announcement:1496319843765583902> ¡Nueva Actualización disponible!\n"
        f"|| <@&1496312737721090278> ||\n"
        f"# ACTUALIZACIÓN {version}\n"
        f"## <:warn:1496319582624026634> ¿QUÉ SE HA AÑADIDO?\n"
        f"{cambios}\n"
        f"# <:link:1496319778758066286> LINK:\n"
        f"{link}"
    )
    await ctx.message.delete()

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Uso correcto: `!update v1.0.0 \"Descripción\" https://tulink.com`")

bot.run(TOKEN)