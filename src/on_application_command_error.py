from bot import bot, discord, traceback
from constants import GUILD_ID, BOTLOG_CHANNEL_ID


@bot.event
async def on_application_command_error(interaction, exception):
    description = f"Channel: {interaction.channel.mention}\nUser: {interaction.user.mention}\nGuild: {interaction.guild.name} ({interaction.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```"
    embed = discord.Embed(title="An Exception Occured", description=description)
    igcse = await bot.fetch_guild(GUILD_ID)
    botlogs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)
    await botlogs.send(embed=embed)
