from bot import bot, discord
from constants import GUILD_ID, BOTLOG_CHANNEL_ID
from monitor_tasks import checklock, checkmute

@bot.event
async def on_ready():
    igcse = bot.get_guild(GUILD_ID)
    botlogs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)    
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="r/IGCSE"))
    checklock.start()
    checkmute.start()    
    try:
        embed = discord.Embed(title=f"Guilds Info ({len(bot.guilds)})", colour=0x3498db, description="Statistics about the servers this bot is in.")
        for guild in bot.guilds:
            value = f"Owner: {guild.owner}\nMembers: {guild.member_count}\nBoosts: {guild.premium_subscription_count}"
            embed.add_field(name=guild.name, value=value, inline=True)
        await botlogs.send(embed=embed)
    except Exception:
        await botlogs.send(f"```py{Exception}````")
