from bot import bot, traceback
from discord import Embed
from constants import GUILD_ID, BOTLOG_CHANNEL_ID

@bot.event
async def on_application_command_error(interaction, exception):
    embed = Embed()

    embed.title = "An exception has occurred!"

    embed.add_field(value=f"channel: {interaction.channel.mention}\nUser: {interaction.user.mention}\nGuild: {interaction.guild.name} ({interaction.guild.id})", inline=False)
    embed.add_field(name="Error", value=f"```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```", inline=False)

    botlogs = bot.get_channel(BOTLOG_CHANNEL_ID)
    await botlogs.send(embed=embed)
