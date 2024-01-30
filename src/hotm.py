from bot import discord, bot, pymongo
from constants import GUILD_ID, LINK, HOTM_VOTING_CHANNEL
from roles import is_helper, is_moderator


@bot.slash_command(description="Vote for the helper of the month", guild_ids=[GUILD_ID])
async def votehotm(
    interaction: discord.Interaction,
    helper: discord.Member = discord.SlashOption(
        name="helper", description="Choose the helper to vote for", required=True
    ),
):
    if helper.bot:
        await interaction.send("You can't vote for a bot.", ephemeral=True)
    elif await is_helper(helper):
        await interaction.response.defer(ephemeral=True)
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        helpers = db.hotmhelpers
        voters = db.hotmvoters

        voter = voters.find_one({"id": interaction.user.id})
        if not voter:
            voter = {"id": interaction.user.id, "votes_left": 2}
            voters.insert_one(voter)
        else:
            if voter["votes_left"] == 0:
                await interaction.send(
                    "You can't vote more than 3 times.", ephemeral=True
                )
                return

            voters.update_one({"id": interaction.user.id}, {"$inc": {"votes_left": -1}})
            voter["votes_left"] = voter["votes_left"] - 1

        await interaction.send(
            f"Done! You have {int(voter['votes_left'])} votes left.", ephemeral=True
        )

        helpers.update_one({"id": helper.id}, {"$inc": {"votes": 1}}, upsert=True)
        hotm_log_channel = bot.get_channel(991202262472998962)
        await hotm_log_channel.send(
            f"{interaction.user} ({interaction.user.id}) has voted for {helper} ({helper.id})"
        )

        messages = [
            msg
            for msg in await bot.get_channel(HOTM_VOTING_CHANNEL).history().flatten()
            if msg.author.id == 861445044790886467
            and msg.content == "HOTM Voting Results"
        ]
        if len(messages) == 0:
            results_message = await bot.get_channel(HOTM_VOTING_CHANNEL).send(
                content="HOTM Voting Results"
            )
        else:
            results_message = messages[0]

        embed = discord.Embed(colour=5111808, description="**Results:**")

        sorted_helpers = helpers.find().sort("votes", -1).limit(10)
        for helper in list(sorted_helpers):
            user_name = interaction.guild.get_member(helper["id"]).name
            embed.add_field(
                name=f"**{user_name}**", value=f"Votes: {helper['votes']}", inline=False
            )
        await results_message.edit(embed=embed)
    else:
        await interaction.send(f"{helper} is not a helper.", ephemeral=True)


@bot.slash_command(
    name="resethotm",
    description="Reset the Helper of the Month data",
    guild_ids=[GUILD_ID],
)
async def resethotm(interaction: discord.Interaction):
    if not await is_moderator(interaction.user):
        await interaction.send(
            "You do not have the necessary permissions to perform this action",
            ephemeral=True,
        )
        return
    await interaction.response.defer(ephemeral=True)
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    db.drop_collection("hotmhelpers")
    db.drop_collection("hotmvoters")
    msgs = [
        msg
        for msg in await bot.get_channel(HOTM_VOTING_CHANNEL).history().flatten()
        if msg.author.id == 861445044790886467 and msg.content == "HOTM Voting Results"
    ]
    await msgs[0].delete()
    await interaction.send("Helper of the Month data has been reset!")
