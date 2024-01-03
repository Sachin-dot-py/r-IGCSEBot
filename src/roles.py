from bot import discord, bot
from constants import GUILD_ID

async def has_role(member: discord.Member, role_name: str):
    roles = [role.name.lower() for role in member.roles]
    role_name_lower = role_name.lower()
    for role in roles:
        if role_name_lower in role:
            return True
    return False

async def get_role(role_name: str):
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name = role_name)
    return role

async def is_moderator(member: discord.Member):
    roles = [role.id for role in member.roles]
    # TODO make these constants?
    if 578170681670369290 in roles or 784673059906125864 in roles:  # r/igcse moderator role ids
        return True
    elif member.guild_permissions.administrator:
        return True
    return False

async def is_server_booster(member: discord.Member):
    return await has_role(member, "Server Booster")

async def is_helper(member: discord.Member):
    return (await has_role(member, "IGCSE Helper") or await has_role(member, 'AS/AL Helper'))
