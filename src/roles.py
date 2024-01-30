from bot import discord, bot
from constants import GUILD_ID, FORCED_MUTE_ROLE, MODERATOR_ROLES, CHAT_MODERATOR_ROLES, BOT_DEVELOPER_ROLES

async def has_role(member: discord.Member, role_name: str):
    for role in member.roles:
        if role.name.lower() == role_name.lower():
            return True
    return False
    
async def get_role(role_name: str):
    guild = bot.get_guild(GUILD_ID)
    return discord.utils.get(guild.roles, name = role_name)

async def is_moderator(member: discord.Member):
    return member.guild_permissions.administrator or MODERATOR_ROLES in [role.id for role in member.roles]

async def is_chat_moderator(member: discord.Member):
    return CHAT_MODERATOR_ROLES in [role.id for role in member.roles]

async def is_bot_developer(member: discord.Member):
    return BOT_DEVELOPER_ROLES in [role.id for role in member.roles]

async def is_server_booster(member: discord.Member):
    return await has_role(member, "Server Booster")

async def is_helper(member: discord.Member):
    return await has_role(member, "IGCSE Helper") or await has_role(member, 'AS/AL Helper')