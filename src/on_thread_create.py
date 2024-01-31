from bot import bot
from constants import GUILD_ID

@bot.event
async def on_thread_create(thread):
    if thread.guild.id == GUILD_ID:
        await thread.join()