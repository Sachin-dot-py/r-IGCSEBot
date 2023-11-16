from constants import LINK, GUILD_ID, LOG_CHANNEL_ID
from bot import discord, bot, traceback

@bot.event
async def on_application_command_error(interaction, exception):
    description = f"Channel: {interaction.channel.mention}\nUser: {interaction.user.mention}\nGuild: {interaction.guild.name} ({interaction.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```"
    embed = discord.Embed(title="An Exception Occured", description=description)
    igcse = await bot.fetch_guild(GUILD_ID)
    logs = await igcse.fetch_channel(LOG_CHANNEL_ID)
    await logs.send(embed=embed)