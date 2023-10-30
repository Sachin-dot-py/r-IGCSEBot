from constants import LINK, GUILD_ID, LOG_CHANNEL_ID
from bot import discord, bot
from checklocks import checklocks

@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(activity=discord.Game(name="u_int"))
    embed = discord.Embed(title=f"Guilds Info ({len(bot.guilds)})", colour=0x3498db, description="Statistics about the servers this bot is in.")
    for guild in bot.guilds:
        value = f"Owner: {guild.owner}\nMembers: {guild.member_count}\nBoosts: {guild.premium_subscription_count}"
        embed.add_field(name=guild.name, value=value, inline=True)
    igcse = await bot.fetch_guild(GUILD_ID)
    logs = await igcse.fetch_channel(LOG_CHANNEL_ID)
    await logs.send(embed=embed)
    for channel in igcse.channels:
        channel_data = discord.Embed(title=channel.name, description=channel.id)
        channel_data.add_field(name="Type", value=str(channel.type))
        channel_data.add_field(name="Category", value=str(channel.category))
        await logs.send(embed=channel_data)
    checklocks.start()