from bot import bot, discord, commands, traceback
from constants import GUILD_ID, BOTLOG_CHANNEL_ID

@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, commands.CommandNotFound):
        return
    description = f"Channel: {ctx.channel.mention}\nUser: {ctx.author.mention}\nGuild: {ctx.guild.name} ({ctx.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```"
    embed = discord.Embed(title="An Exception Occured", description=description)
    igcse = await bot.fetch_guild(GUILD_ID)
    botlogs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)
    await botlogs.send(embed=embed)