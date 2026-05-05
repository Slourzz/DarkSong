import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import aiohttp
import asyncio
import json

load_dotenv()
TOKEN = os.getenv('TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

UPDATE_CHANNEL_ID = 1500691578916962344
GITHUB_REPO = "Slourzz/DarkSong"
ROL_ID = 1496312737721090278
VERSION_FILE = "last_version.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

COLORS = {
    "stable": 0x2ecc71,
    "update": 0x3498db,
    "beta":   0xf1c40f,
    "hotfix": 0xe74c3c
}

tz_mexico = timezone(timedelta(hours=-6))

def get_last_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return json.load(f).get("version", None)
    except:
        return None

def save_last_version(version):
    with open(VERSION_FILE, "w") as f:
        json.dump({"version": version}, f)

def get_color(tag):
    tag = tag.lower()
    if "hotfix" in tag:
        return COLORS["hotfix"]
    elif "beta" in tag:
        return COLORS["beta"]
    elif "stable" in tag:
        return COLORS["stable"]
    else:
        return COLORS["update"]

async def check_github_releases():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        version = data["tag_name"]
                        nombre = data["name"]
                        last_version = get_last_version()

                        if version != last_version:
                            save_last_version(version)
                            channel = bot.get_channel(UPDATE_CHANNEL_ID)
                            if channel:
                                fecha = datetime.now(tz_mexico).strftime("%d/%m/%y")
                                cambios = data["body"] or "Sin descripción."
                                link_repo = data["html_url"]

                                link_apk = link_repo
                                for asset in data.get("assets", []):
                                    if asset["name"].endswith(".apk"):
                                        link_apk = asset["browser_download_url"]
                                        break

                                color = get_color(version)

                                embed = discord.Embed(
                                    description=(
                                        f"# 🚀 NUEVA ACTUALIZACIÓN DISPONIBLE\n"
                                        f"### DarkSong {nombre}\n\n"
                                        f"### 📅 {fecha}\n\n"
                                        f"## ✨ Novedades\n"
                                        f"{cambios}\n\n"
                                        f"## ⬆️ Nueva versión: {version}\n"
                                        f"## 📦 Versión anterior: {last_version or 'N/A'}"
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
                                    url=f"https://github.com/{GITHUB_REPO}"
                                ))

                                await channel.send(f"<@&{ROL_ID}>", embed=embed, view=row)

        except Exception as e:
            print(f"Error al revisar releases: {e}")

        await asyncio.sleep(300)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    bot.loop.create_task(check_github_releases())

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx, tipo: str, version: str, version_anterior: str, cambios: str, link_apk: str, link_repo: str):
    
    channel = bot.get_channel(UPDATE_CHANNEL_ID)
    
    if channel is None:
        await ctx.send("❌ No encontré el canal de anuncios.")
        return

    color = COLORS.get(tipo.lower(), 0x3498db)
    fecha = datetime.now(tz_mexico).strftime("%d/%m/%y")

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

    await channel.send(f"<@&{ROL_ID}>", embed=embed, view=row)
    await ctx.message.delete()

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Uso correcto: `!update [tipo] [versión] [versión_anterior] \"Cambios\" [link_apk] [link_repo]`\n**Tipos:** stable, update, beta, hotfix")

bot.run(TOKEN)