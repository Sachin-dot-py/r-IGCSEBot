from bot import discord, bot

async def is_banned(user, guild):
    try:
        await guild.fetch_ban(user)
        return True
    except:
        return False
