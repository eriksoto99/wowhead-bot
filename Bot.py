import discord
import os
import feedparser
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Servidor Flask para mantener el bot activo
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Cargar variables del entorno
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
RSS_URL = os.getenv("RSS_URL")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

posted_links = set()

@client.event
async def on_ready():
    print(f"🟢 Bot conectado como {client.user}")
    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send("📝 Prueba: el bot puede enviar mensajes correctamente.")

async def check_feed():
    await client.wait_until_ready()
    channel = await client.fetch_channel(CHANNEL_ID)

    while True:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries[:10]:
            title = entry.title.lower()
            summary = entry.summary.lower()

            if ("cataclysm" in title or "cataclysm" in summary or
                "mists of pandaria" in title or "mists of pandaria" in summary):

                if entry.link not in posted_links:
                    message = f"📰 **{entry.title}**\n{entry.summary}\n{entry.link}"
                    await channel.send(message)
                    posted_links.add(entry.link)

        await asyncio.sleep(300)

async def main():
    keep_alive()  # Activa el servidor Flask
    async with client:
        asyncio.create_task(check_feed())
        await client.start(TOKEN)

asyncio.run(main())
