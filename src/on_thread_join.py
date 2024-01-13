from bot import bot

@bot.event
async def on_thread_join(thread):
    await thread.join()