from bot import bot, discord
from constants import GUILD_ID


@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id == GUILD_ID:
        if before.channel:
            if (
                "study session" in before.channel.name.lower()
                and before.channel.members == []
            ):
                await before.channel.edit(name="General")
