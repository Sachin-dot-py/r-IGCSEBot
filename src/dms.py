from bot import bot, discord, commands
from mongodb import dmsdb
from roles import is_chat_moderator, is_moderator
from constants import GUILD_ID, DMS_CLOSED_CHANNEL_ID

async def send_dm(member: discord.Member, **kwargs):
    try:
        await member.send(**kwargs)
    except:
        if member.guild.id == GUILD_ID:
            thread = await dmsdb.get_thread(member)
            await thread.send(**kwargs)
            await thread.send(content=member.mention)

@bot.command(name = "Delete DM thread")
@commands.guild_only()
async def delete_dm_thread(ctx, member: discord.Member = None):
    if ctx.guild.id != GUILD_ID:
        return
    
    if not member:
        if not await is_moderator(ctx.author) and not await is_chat_moderator(ctx.author):
            await ctx.send(f"You are not permitted to use this command, {member.mention}!")
            return
    else:
        member = ctx.author # Guaranteed to be discord.Member
    
    thread = await dmsdb.get_thread(member, False)

    if not thread:
        await ctx.send("No thread found!")
    else:
        await dmsdb.del_thread(thread)
        await ctx.send("DM thread deleted! If DMs are still closed, a new thread will be made.")