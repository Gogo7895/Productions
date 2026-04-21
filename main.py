import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError(
        "Problème"
    )

from bot.discord_bot import bot
bot.run(TOKEN)
