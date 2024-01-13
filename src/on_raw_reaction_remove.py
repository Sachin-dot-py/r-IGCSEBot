from bot import bot, discord
from constants import GUILD_ID
from mongodb import rrdb

@bot.event
async def on_raw_reaction_remove(reaction):
    guild = bot.get_guild(GUILD_ID)
    user = await guild.fetch_member(reaction.user_id)
    if user.bot:
        return
    is_rr = rrdb.get_rr(str(reaction.emoji), reaction.message_id)
    if is_rr is not None:
        role = guild.get_role(is_rr["role"])
        await user.remove_roles(role)
    
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)

    vote = 0 
    for reaction in message.reactions:
        if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            async for user in reaction.users():
                if user == bot.user:
                    vote += 1
                    break

    if vote == 2:
        for reaction in message.reactions:
            if str(reaction.emoji) == "✅":
                yes = reaction.count - 1
            if str(reaction.emoji) == "❌":
                no = reaction.count - 1
        try:
            yes_p = round((yes / (yes + no)) * 100) // 10
            no_p = 10 - yes_p
        except:
            yes_p = 10
            no_p = 0
        description = f"Total Votes: {yes + no}\n\n{yes_p * 10}% {yes_p * '🟩'}{no_p * '🟥'} {no_p * 10}%\n"
        description += "\n".join(message.embeds[0].description.split("\n")[3:])
        embed = discord.Embed(title=message.embeds[0].title, colour=message.embeds[0].colour, description=description)
        for field in message.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await message.edit(embed=embed)