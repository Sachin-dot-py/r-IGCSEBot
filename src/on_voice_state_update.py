from constants import GUILD_ID
from bot import bot

@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id == GUILD_ID:
        if before.channel:  # When user leaves a voice channel
            if "study session" in before.channel.name.lower() and before.channel.members == []:  # If the study session is over
                await before.channel.edit(name="General")  # Reset channel name