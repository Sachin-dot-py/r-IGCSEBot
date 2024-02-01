from bot import bot, traceback
from constants import GUILD_ID, BOTLOG_CHANNEL_ID

@bot.event
async def on_application_command_error(interaction, exception):
    description = f"Channel: {ctx.channel.mention}\nUser: {ctx.author.mention}\nGuild: {ctx.guild.name} ({ctx.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```}    
    embed = discord.Embed(title="An Exception Occured", description=description)
    botlogs = bot.get_channel(BOTLOG_CHANNEL_ID)
    await botlogs.send(embed=embed)
