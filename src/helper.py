from bot import discord

async def isHelper(member: discord.Member):
    if await hasRole(member, "IGCSE Helper") or await hasRole(member, 'AS/AL Helper'):
        return True
    return False