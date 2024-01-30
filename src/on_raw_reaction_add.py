from bot import discord, bot, requests
from constants import GUILD_ID
from mongodb import gpdb, rrdb
from roles import is_moderator


@bot.event
async def on_raw_reaction_add(reaction):
    guild = bot.get_guild(GUILD_ID)
    user = await guild.fetch_member(reaction.user_id)
    if user.bot:
        return
    is_rr = rrdb.get_rr(str(reaction.emoji), reaction.message_id)
    if is_rr is not None:
        role = guild.get_role(is_rr["role"])
        await user.add_roles(role)

    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)

    author = message.channel.guild.get_member(reaction.user_id)
    if author.bot or not await is_moderator(author):
        return

    if (
        message.channel.id == gpdb.get_pref("emote_channel", reaction.guild_id)
        and str(reaction.emoji) == "🔒"
    ):
        upvotes = 0
        downvotes = 0
        for r in message.reactions:
            if r.emoji == "👍":
                upvotes += r.count
            elif r.emoji == "👎":
                downvotes += r.count
        name = message.content[
            message.content.find(":")
            + 1 : message.content.find(":", message.content.find(":") + 1)
        ]
        if upvotes / downvotes >= 3:
            emoji = await message.guild.create_custom_emoji(
                name=name, image=requests.get(message.attachments[0].url).content
            )
            await message.reply(
                f"The submission by {message.mentions[0]} for the emote {str(emoji)} has passed."
            )
        else:
            await message.reply(
                f"The submission by {message.mentions[0]} for the emote `:{name}:`has failed."
            )

    if (
        str(reaction.emoji) == "🟢"
        and reaction.user_id != bot.user.id
        and message.channel.id
        == gpdb.get_pref("suggestions_channel", reaction.guild_id)
    ):
        author = message.channel.guild.get_member(reaction.user_id)
        if await is_moderator(author):
            description = message.embeds[0].description
            embed = discord.Embed(
                title=message.embeds[0].title,
                colour=message.embeds[0].colour,
                description=description,
            )
            for field in message.embeds[0].fields:
                if field.name == "Accepted ✅":
                    return
                if field.name != "Rejected ❌":
                    try:
                        embed.add_field(
                            name=field.name, value=field.value, inline=False
                        )
                    except:
                        pass
            embed.add_field(
                name="Accepted ✅",
                value=f"This suggestion has been accepted by the moderators. ({author})",
                inline=False,
            )
            await message.edit(embed=embed)
            await message.pin()
        return

    if (
        str(reaction.emoji) == "🔴"
        and reaction.user_id != bot.user.id
        and message.channel.id
        == gpdb.get_pref("suggestions_channel", reaction.guild_id)
    ):
        author = message.channel.guild.get_member(reaction.user_id)
        if await is_moderator(author):
            description = message.embeds[0].description
            embed = discord.Embed(
                title=message.embeds[0].title,
                colour=message.embeds[0].colour,
                description=description,
            )
            for field in message.embeds[0].fields:
                if field.name == "Rejected ❌":
                    return
                if field.name != "Accepted ✅":
                    try:
                        embed.add_field(
                            name=field.name, value=field.value, inline=False
                        )
                    except:
                        pass
            embed.add_field(
                name="Rejected ❌",
                value=f"This suggestion has been rejected by the moderators. ({author})",
                inline=False,
            )
            await message.edit(embed=embed)
        return

    vote = 0
    for reaction in message.reactions:
        if str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌":
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
        embed = discord.Embed(
            title=message.embeds[0].title,
            colour=message.embeds[0].colour,
            description=description,
        )
        for field in message.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await message.edit(embed=embed)
