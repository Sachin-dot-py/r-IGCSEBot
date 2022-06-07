import datetime
import time
import pymongo
import nextcord as discord
from nextcord.ext import commands
import requests
import os

# Set up Discord API Token and MongoDB Access Link in a .env file and use the command "heroku local" to run the bot locally.

TOKEN = os.environ.get("IGCSEBOT_TOKEN")
LINK = os.environ.get("MONGO_LINK")
GUILD_ID = 576460042774118420

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=".", intents=intents)
keywords = {}


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Flynn#5627"))


@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id == 576460042774118420:
        if before.channel:  # When user leaves a voice channel
            if "study session" in before.channel.name.lower() and before.channel.members == []:  # If the study session is over
                await before.channel.edit(name="General")  # Reset channel name


@bot.event
async def on_raw_reaction_add(reaction):
    # Suggestions voting
    channel = bot.get_channel(reaction.channel_id)
    msg = await channel.fetch_message(reaction.message_id)
    if str(reaction.emoji) == "🟢" and reaction.user_id != bot.user.id and msg.channel.id == gpdb.get_pref(
            "suggestions_channel", reaction.guild_id):  # Suggestion accepted by mod in #suggestions-voting
        author = msg.channel.guild.get_member(reaction.user_id)
        if await isModerator(author):
            description = msg.embeds[0].description
            embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
            for field in msg.embeds[0].fields:
                if field.name == "Accepted ✅":
                    return
                if field.name != "Rejected ❌":
                    try:
                        embed.add_field(name=field.name, value=field.value, inline=False)
                    except:
                        pass
            embed.add_field(name="Accepted ✅", value=f"This suggestion has been accepted by the moderators. ({author})",
                            inline=False)
            await msg.edit(embed=embed)
            await msg.pin()
        return

    if str(
            reaction.emoji) == "🔴" and reaction.user_id != bot.user.id and msg.channel.id == gpdb.get_pref(
        "suggestions_channel", reaction.guild_id):  # Suggestion rejected by mod in #suggestions-voting
        author = msg.channel.guild.get_member(reaction.user_id)
        if await isModerator(author):
            description = msg.embeds[0].description
            embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
            for field in msg.embeds[0].fields:
                if field.name == "Rejected ❌":
                    return
                if field.name != "Accepted ✅":
                    try:
                        embed.add_field(name=field.name, value=field.value, inline=False)
                    except:
                        pass
            embed.add_field(name="Rejected ❌", value=f"This suggestion has been rejected by the moderators. ({author})",
                            inline=False)
            await msg.edit(embed=embed)
        return

    # Suggestion voting system
    vote = 0
    for reaction in msg.reactions:
        if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            async for user in reaction.users():
                if user == bot.user:
                    vote += 1
                    break

    if vote == 2:
        for reaction in msg.reactions:
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
        description += "\n".join(msg.embeds[0].description.split("\n")[3:])
        embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
        for field in msg.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await msg.edit(embed=embed)


@bot.event
async def on_raw_reaction_remove(reaction):
    channel = bot.get_channel(reaction.channel_id)
    msg = await channel.fetch_message(reaction.message_id)

    vote = 0  # Suggestions voting system - remove vote
    for reaction in msg.reactions:
        if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            async for user in reaction.users():
                if user == bot.user:
                    vote += 1
                    break

    if vote == 2:
        for reaction in msg.reactions:
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
        description += "\n".join(msg.embeds[0].description.split("\n")[3:])
        embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
        for field in msg.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await msg.edit(embed=embed)


@bot.event
async def on_thread_join(thread):
    await thread.join()  # Join all threads automatically


@bot.event
async def on_guild_join(guild):
    global gpdp
    gpdp.set_pref('rep_enabled', True, guild.id)
    await guild.create_role(name="Reputed", color=0x3498db)  # Create Reputed Role
    await guild.create_role(name="100+ Rep Club", color=0xf1c40f)  # Create 100+ Rep Club Role
    await guild.create_role(name="500+ Rep Club", color=0x2ecc71)  # Create 500+ Rep Club Role
    await guild.system_channel.send(
        "Hi! Please set server preferences using the slash command /set_preferences for this bot to function properly.")


@bot.event
async def on_member_join(member):
    if member.guild.id == 576460042774118420:  # r/igcse welcome message
        embed1 = discord.Embed.from_dict(eval(
            r"""{'color': 3066993, 'type': 'rich', 'description': "Hello and welcome to the official r/IGCSE Discord server, a place where you can ask any doubts about your exams and find help in a topic you're struggling with! We strongly suggest you read the following message to better know how our server works!\n\n***How does the server work?***\n\nThe server mostly entirely consists of the students who are doing their IGCSE and those who have already done their IGCSE exams. This server is a place where you can clarify any of your doubts regarding how exams work as well as any sort of help regarding a subject or a topic in which you struggle.\n\nDo be reminded that academic dishonesty is not allowed in this server and you may face consequences if found to be doing so. Examples of academic dishonesty are listed below (the list is non-exhaustive) - by joining the server you agree to follow the rules of the server.\n\n> Asking people to do your homework for you, sharing any leaked papers before the exam session has ended, etc.), asking for leaked papers or attempted malpractice are not allowed as per *Rule 1*. \n> \n> Posting pirated content such as textbooks or copyrighted material are not allowed in this server as per *Rule 7.*\n\n***How to ask for help?***\n\nWe have subject helpers for every subject to clear any doubts or questions you may have. If you want a subject helper to entertain a doubt, you should type in `'helper'`. A timer of **15 minutes** will start before the respective subject helper will be pinged. Remember to cancel your ping once a helper is helping you!\n\n***How to contact the moderators?***\n\nYou can contact us by sending a message through <@861445044790886467> by responding to the bot, where it will be forwarded to the moderators to view. Do be reminded that only general server inquiries should be sent and other enquiries will not be entertained, as there are subject channels for that purpose.", 'title': 'Welcome to r/IGCSE!'}"""))
        # embed2 = discord.Embed.from_dict(eval(
        #     r"{'color': 3066993, 'type': 'rich', 'description': 'We also require all new users to pick up session roles. These make sure that you will have access to the appropriate general chat channels and for our helpers to give you more specific advice.\n\nReact to the corresponding reactions in <#932550807755304990> to verify and gain access to the rest of the server.\n\nAfterwards, react to the corresponding roles in <#932570912660791346> or <#932546951055032330> to gain access to your corresponding subject channels.', 'title': 'Verification system (PLEASE READ)'}"))
        channel = await member.create_dm()
        try:
            await channel.send(embed=embed1)
            # await channel.send(embed=embed2)
        except:
            channel = member.guild.get_channel(920138547858645072)
            await channel.send(content=member.mention, embed=embed1)
            # await channel.send(content=member.mention, embed=embed2)


@bot.event
async def on_message(message):
    if message.author.bot: return

    if gpdb.get_pref('rep_enabled', message.guild.id):
        await repMessages(message)  # If message is replying to another message
    if message.channel.name == 'counting':  # To facilitate #counting
        await counting(message)
    if message.guild.id == 576460042774118420:
        if message.content.lower() == "pin":  # Pin a message
            if isHelper(message.author) or isModerator(message.author):
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.pin()
                await msg.reply(f"This message has been pinned by {message.author.mention}.")
                await message.delete()

        if message.content.lower() == "unpin":  # Unpin a message
            if isHelper(message.author) or isModerator(message.author):
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.unpin()
                await msg.reply(f"This message has been unpinned by {message.author.mention}.")
                await message.delete()

    global keywords
    if not keywords.get(message.guild.id, None):  # on first message from guild
        keywords[message.guild.id] = kwdb.get_keywords(message.guild.id)
    if message.content.lower() in keywords[message.guild.id].keys():
        await message.channel.send(keywords[message.guild.id][message.content.lower()])


# Utility Functions

async def isModerator(member: discord.Member):
    roles = [role.id for role in member.roles]
    if 578170681670369290 in roles or 784673059906125864 in roles:  # r/igcse moderator role ids
        return True
    elif member.guild_permissions.administrator:
        return True
    return False


async def isHelper(member: discord.Member):
    roles = [role.name.lower() for role in member.roles]
    for role in roles:
        if "helper" in role:
            return True
    return False


# Reaction Roles

helper_roles = {
    576463745073807372: 696688133844238367,
    576463729802346516: 696415409720786994,
    576463717844254731: 696415478331211806,
    576461721900679177: 697031993820446720,
    576463988506886166: 697032184451563530,
    579288532942848000: 854000279933812737,
    579292149678342177: 697032265624060005,
    576464244455899136: 863699698234032168,
    576463493646123025: 697031812102225961,
    576463562084581378: 697031148685230191,
    576463593562701845: 697090437520949288,
    579386214218465281: 888382475645120575,
    576463609325158441: 776986644757610517,
    576463682054389791: 697031853369983006,
    576461701332074517: 697030773814853633,
    576463472544710679: 697030911023120455,
    871702123505655849: 871702647223255050,
    576463638983082005: 697031447021748234,
    868056343871901696: 697031555457220673,
    576463799582851093: 697031087985262612,
    576463769526599681: 697030991205892156,
    576463668808646697: 697407528685797417,
    576464116336689163: 697031043089170463,
    576463907485646858: 697031773435068466,
    871589653315190845: 848529485351223325,
    576463811327033380: 697031605100740698,
    576463820575211560: 697031649233338408,
    576463893858222110: 697031735086546954,
    576463832168398852: 697031692115771513,
    871590306338971678: 871588409032990770,
    886883608504197130: 886884656845312020,
    576464270041022467: 863691773628907560,
    697072778553065542: 578170681670369290,
    929349933432193085: 929422215940825088,
    947859228649992213: 949941010430033950,  # Test channel/role
}


class DropdownRR(discord.ui.Select):
    def __init__(self, category, options):
        self._options = options
        selectOptions = [
            discord.SelectOption(emoji=option[0], label=option[1], value=option[2]) for option in options
        ]
        super().__init__(placeholder=f'Select your {category} subjects', min_values=0, max_values=len(selectOptions),
                         options=selectOptions)

    async def callback(self, interaction: discord.Interaction):
        added_role_names = []
        removed_role_names = []
        for option in self._options:
            role = interaction.guild.get_role(int(option[2]))
            if str(option[2]) in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
                    added_role_names.append(role.name)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    removed_role_names.append(role.name)
        if len(added_role_names) > 0 and len(removed_role_names) > 0:
            await interaction.send(
                f"Successfully opted for roles: {', '.join(added_role_names)} and unopted from roles: {', '.join(removed_role_names)}.",
                ephemeral=True)
        elif len(added_role_names) > 0 and len(removed_role_names) == 0:
            await interaction.send(f"Successfully opted for roles: {', '.join(added_role_names)}.", ephemeral=True)
        elif len(added_role_names) == 0 and len(removed_role_names) > 0:
            await interaction.send(f"Successfully unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)


class DropdownViewRR(discord.ui.View):
    def __init__(self):
        super().__init__()
        data = {
            "Sciences": [
                ["💡", "Physics", 685837416443281493],
                ["🧪", "Chemistry", 685837450895032336],
                ["🍀", "Biology", 685837475939221770],
                ["🔍", "Coordinated and Combined Sciences", 667769546475700235],
                ["🌲", "Environmental Management", 688357525984509984],
                ["🏃‍♂️", "Physical Education", 685837363003523097],
            ],
            "Mathematics": [
                ["🔢", "Mathematics", 688354722251276308],
                ["✳️", "Additional/Further Mathematics", 688355303808303170],
                ["♾️", "International Mathematics", 871702273640787988],
            ],
            # Add other subjects here
        }
        for category, options in data.items():
            self.add_item(DropdownRR(category, options))


@bot.slash_command(description="Pick up your roles", guild_ids=[GUILD_ID])
async def roles(interaction: discord.Interaction):
    await interaction.send(view=DropdownViewRR(), ephemeral=True)


@bot.command(description="Dropdown for picking up reaction roles", guild_ids=[GUILD_ID])
async def roles(ctx):
    await ctx.send(view=DropdownViewRR())


# Suggestions
@bot.slash_command(description="Make a new suggestion for the server")
async def suggest(interaction: discord.Interaction,
                  suggestion: str = discord.SlashOption(name="suggestion",
                                                        description="Create a new suggestion for the server.",
                                                        required=True),
                  ):
    channel_id = gpdb.get_pref("suggestions_channel", interaction.guild.id)
    if not channel_id:
        await interaction.send(
            "The suggestions channel for this server is not set. Please ask a moderator/admin to set it using /set_preferences to use this command.",
            ephemeral=True)
    else:
        await interaction.response.defer(ephemeral=True)
        channel = bot.get_channel(channel_id)
        embedVar = discord.Embed(title=f"Suggestion by {interaction.user}",
                                 description=f"Total Votes: 0\n\n{'🟩' * 10}\n\nSuggestion: {suggestion}",
                                 colour=discord.Colour.green())
        msg = await channel.send(embed=embedVar)
        await msg.add_reaction('✅')
        await msg.add_reaction("🟢")
        await msg.add_reaction("🔴")
        await msg.add_reaction('❌')
        await msg.create_thread(name=f"Suggestion by {interaction.user} Discussion")
        await interaction.send(f"This suggestion has been sent in {channel.mention}", ephemeral=True)


# Helper

class CancelPingBtn(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15 * 60)
        self.value = None

    @discord.ui.button(label="Cancel Ping", style=discord.ButtonStyle.blurple)
    async def cancel_ping_btn(self, button: discord.ui.Button, interaction_b: discord.Interaction):
        self.cancel_user = interaction_b.user
        button.disabled = True
        self.stop()



@bot.slash_command(description="Ping a helper in any subject channel", guild_ids=[GUILD_ID])
async def helper(interaction: discord.Interaction):
    try:
        helper_role = discord.utils.get(interaction.guild.roles, id=helper_roles[interaction.channel.id])
    except:
        await interaction.send("There are no helper roles specified for this channel.", ephemeral=True)
        return
    await interaction.response.defer()
    roles = [role.name.lower() for role in interaction.user.roles]
    if "server booster" in roles:
        await interaction.send(f"{helper_role.mention}\n(Requested by {interaction.user.mention})")
        return
    view = CancelPingBtn()
    await interaction.send(
        f"The helper role for this channel, `@{helper_role.name}`, will automatically be pinged (<t:{int(time.time() + 15 * 60)}:R>). If your query has been resolved by then, please click on the `Cancel Ping` button",
        view=view)
    timeout = await view.wait()
    if timeout:
        await interaction.send(f"{helper_role.mention}\n(Requested by {interaction.user.mention})")
    else:
        await interaction.edit_original_message(content=f"Ping cancelled by {view.cancel_user}")


@bot.command(name="refreshhelpers", description="Refresh the helper count in the description of subject channels",
             guild_ids=[GUILD_ID])
async def refreshhelpers(ctx):
    if ctx.message.content.lower() == "refresh helpers":  # Refresh number of helpers info in description of channel
        changed = []
        for chnl, role in helper_roles.items():
            try:
                helper_role = discord.utils.get(ctx.message.guild.roles, id=role)
                no_of_users = len(helper_role.members)
                channel = bot.get_channel(chnl)
                new_topic = None
                for line in channel.topic.split("\n"):
                    if "No. of helpers" in line:
                        new_topic = channel.topic.replace(line, f"No. of helpers: {no_of_users}")
                        break
                else:
                    new_topic = f"{channel.topic}\nNo. of helpers: {no_of_users}"
                if channel.topic != new_topic:
                    await channel.edit(topic=new_topic)
                    changed.append(channel.mention)
            except:
                continue
        if changed:
            await ctx.message.reply("Done! Changed channels: " + ", ".join(changed))
        else:
            await ctx.message.reply("No changes were made.")


# Reputation


class ReputationDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.reputation = self.db.reputation

    def bulk_insert_rep(self, rep_dict: dict, guild_id: int):
        # rep_dict = eval("{DICT}".replace("\n","")) to restore reputation from #rep-backup
        insertion = [{"user_id": user_id, "rep": rep, "guild_id": guild_id} for user_id, rep in rep_dict.items()]
        result = self.reputation.insert_many(insertion)
        return result

    def get_rep(self, user_id: int, guild_id: int):
        result = self.reputation.find_one({"user_id": user_id, "guild_id": guild_id})
        if result is None:
            return None
        else:
            return result['rep']

    def change_rep(self, user_id: int, new_rep: int, guild_id: int):
        result = self.reputation.update_one({"user_id": user_id, "guild_id": guild_id}, {"$set": {"rep": new_rep}})
        return new_rep

    def delete_user(self, user_id: int, guild_id: int):
        result = self.reputation.delete_one({"user_id": user_id, "guild_id": guild_id})
        return result

    def add_rep(self, user_id: int, guild_id: int):
        rep = self.get_rep(user_id, guild_id)
        if rep is None:
            rep = 1
            self.reputation.insert_one({"user_id": user_id, "guild_id": guild_id, "rep": rep})
        else:
            rep += 1
            self.change_rep(user_id, rep, guild_id)
        return rep

    def rep_leaderboard(self, guild_id):
        leaderboard = self.reputation.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0}).sort("rep", -1)
        return list(leaderboard)


repDB = ReputationDB(LINK)


async def isThanks(text):
    alternatives = ['thanks', 'thank you', 'thx', 'tysm', 'thank u', 'thnks', 'tanks', "thanku"]
    if "ty" in text.lower().split():
        return True
    else:
        for alternative in alternatives:
            if alternative in text.lower():
                return True


async def isWelcome(text):
    alternatives = ["you're welcome", "your welcome", "ur welcome", "your welcome", 'no problem']
    alternatives_2 = ["np", "np!", "yw", "yw!"]
    if "welcome" == text.lower():
        return True
    else:
        for alternative in alternatives:
            if alternative in text.lower():
                return True
        for alternative in alternatives_2:
            if alternative in text.lower().split() or alternative == text.lower():
                return True
    return False


async def repMessages(message):
    repped = []
    if message.reference:
        msg = await message.channel.fetch_message(message.reference.message_id)

    if message.reference and msg.author != message.author and not msg.author.bot and not message.author.mentioned_in(
            msg) and (
            await isWelcome(message.content)):
        repped = [message.author]
    elif await isThanks(message.content):
        for mention in message.mentions:
            if mention == message.author:
                await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep yourself!")
            elif mention.bot:
                await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep a bot!")
            else:
                repped.append(mention)

    if repped:
        for user in repped:
            rep = repDB.add_rep(user.id, message.guild.id)
            if rep == 100 or rep == 500:
                role = discord.utils.get(user.guild.roles, name=f"{rep}+ Rep Club")
                await user.add_roles(role)
                await message.channel.send(f"Gave +1 Rep to {user.mention} ({rep})\nWelcome to the {rep}+ Rep Club!")
            else:
                await message.channel.send(f"Gave +1 Rep to {user} ({rep})")
        leaderboard = repDB.rep_leaderboard(message.guild.id)
        members = [list(item.values())[0] for item in leaderboard[:3]]  # Creating list of Reputed member ids
        role = discord.utils.get(message.guild.roles, name="Reputed")
        if [member.id for member in role.members] != members:  # If Reputed has changed
            for m in role.members:
                await m.remove_roles(role)
            for member in members:
                member = message.guild.get_member(member)
                await member.add_roles(role)


@bot.slash_command(description="View someone's current rep")
async def rep(interaction: discord.Interaction,
              user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=True)):
    await interaction.response.defer()
    rep = repDB.get_rep(user.id, interaction.guild.id)
    await interaction.send(f"{user} has {rep} rep.", ephemeral=False)


@bot.slash_command(description="Change someone's current rep (for moderators)")
async def change_rep(interaction: discord.Interaction,
                     user: discord.User = discord.SlashOption(name="user", description="User to view rep of",
                                                              required=True),
                     new_rep: int = discord.SlashOption(name="new_rep", description="New rep amount", required=True, min_value=1, max_value=9999)):
    if await isModerator(interaction.user):
        await interaction.response.defer()
        rep = repDB.change_rep(user.id, new_rep, interaction.guild.id)
        await interaction.send(f"{user} now has {rep} rep.", ephemeral=False)
    else:
        await interaction.send(f"You are not authorized to use this command.", ephemeral=True)


@bot.slash_command(description="View the current rep leaderboard")
async def leaderboard(interaction: discord.Interaction,
                      page: int = discord.SlashOption(name="page", description="Page number to to display",
                                                      required=False, min_value=1, max_value=99999),
                      user_to_find: discord.User = discord.SlashOption(name="user",
                                                                       description="User to find on the leaderboard",
                                                                       required=False)
                      ):
    await interaction.response.defer()
    leaderboard = repDB.rep_leaderboard(interaction.guild.id)  # Rep leaderboard
    leaderboard = [item.values() for item in leaderboard]  # Changing format of leaderboard
    chunks = [list(leaderboard)[x:x + 9] for x in
              range(0, len(leaderboard), 9)]  # Split into groups of 9

    pages = []
    for n, chunk in enumerate(chunks):
        embedVar = discord.Embed(title="Reputation Leaderboard", description=f"Page {n + 1} of {len(chunks)}",
                                 colour=discord.Colour.green())
        for user, rep in chunk:
            if user_to_find:
                if user_to_find.id == user:
                    page = n + 1
            user_name = interaction.guild.get_member(user)
            if rep == 0 or user_name is None:
                repDB.delete_user(user, interaction.guild.id)
            else:
                embedVar.add_field(name=user_name, value=str(rep) + "\n", inline=True)
        pages.append(embedVar)

    if not page: page = 1

    message = await interaction.send(embed=pages[page - 1])


# Keywords

class KeywordsDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.keywords = self.db.keywords

    # def bulk_insert_keywords(self, rep_dict: dict, guild_id: int):
    #     # rep_dict = eval("{DICT}".replace("\n","")) to restore reputation from #rep-backup
    #     insertion = [{"user_id": user_id, "rep": rep, "guild_id": guild_id} for user_id, rep in rep_dict.items()]
    #     result = self.reputation.insert_many(insertion)
    #     return result

    def get_keywords(self, guild_id: int):
        result = self.keywords.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0})
        return {i['keyword'].lower(): i['autoreply'] for i in result}

    def add_keyword(self, keyword: str, autoreply: str, guild_id: int):
        result = self.keywords.insert_one({"keyword": keyword, "autoreply": autoreply, "guild_id": guild_id})
        return result

    def remove_keyword(self, keyword: str, guild_id: int):
        result = self.keywords.delete_one({"keyword": keyword, "guild_id": guild_id})
        return result


kwdb = KeywordsDB(LINK)


@bot.command(name="addkeyword", description="Add keywords (for mods)")
async def addkeyword(ctx, keyword: str, autoresponse: str):
    """ Put keyword and autoresponse in quotation marks and put a space between them"""
    if not await isModerator(ctx.author):
        await ctx.reply("You do not have the permissions to perform this action.")
    kwdb.add_keyword(keyword, autoresponse, ctx.guild.id)
    global keywords
    keywords[ctx.guild.id] = kwdb.get_keywords(ctx.guild.id)
    await ctx.reply(f"Created keyword {keyword} for autoresponse {autoresponse}")


@bot.command(name="deletekeyword", description="Delete keywords (for mods)")
async def deletekeyword(ctx, keyword: str):
    """ Put keyword in quotation marks"""
    if not await isModerator(ctx.author):
        await ctx.reply("You do not have the permissions to perform this action.")
    kwdb.remove_keyword(keyword, ctx.guild.id)
    global keywords
    keywords[ctx.guild.id] = kwdb.get_keywords(ctx.guild.id)
    await ctx.reply(f"Deleted keyword {keyword}")


@bot.command(name="listkeywords", description="List keywords (for mods)")
async def listkeywords(ctx):
    """ Put keyword in quotation marks"""
    if not await isModerator(ctx.author):
        await ctx.reply("You do not have the permissions to perform this action.")
    await ctx.reply(f"Active keywords: {kwdb.get_keywords(ctx.guild.id).keys()}")


# Misc Functions

@bot.command(description="Clear messages in a channel")
async def clear(ctx, num_to_clear: int):
    if not await isModerator(ctx.author):
        await ctx.reply("You do not have the permissions to perform this action.")
    try:
        await ctx.channel.purge(limit=num_to_clear + 1)
    except:
        await ctx.reply("Oops! I can only delete messages sent in the last 14 days")


async def counting(message):
    if message.author.bot:
        await message.delete()
        return

    msgs = await message.channel.history(limit=2).flatten()
    try:
        msg = msgs[1]

        if "✅" in [str(reaction.emoji) for reaction in msg.reactions]:
            last_number = int(msg.content)
            last_author = msg.author
        else:
            last_number = 0
            last_author = None
    except:
        last_number = 0
        last_author = None

    try:
        if int(message.content) == last_number + 1 and last_author != message.author:
            await message.add_reaction("✅")
        else:
            await message.delete()
    except:
        await message.delete()


@bot.slash_command(description="Send messages using the bot (for mods)")
async def send_message(interaction: discord.Interaction,
                       message_text: str = discord.SlashOption(name="message_text",
                                                               description="Message to send",
                                                               required=True),
                       channel_to_send_to: discord.abc.GuildChannel = discord.SlashOption(name="channel_to_send_to",
                                                                                          description="Channel to send the message to",
                                                                                          required=True),
                       message_id_to_reply_to: str = discord.SlashOption(name="message_id_to_reply_to",
                                                                         description="Message to reply to (optional)",
                                                                         required=False)):
    if not await isModerator(interaction.user):
        await interaction.send("You are not authorized to perform this action.")
        return
    await interaction.response.defer(ephemeral=True)
    if message_id_to_reply_to:
        message_to_reply_to = await channel_to_send_to.fetch_message(int(message_id_to_reply_to))
        await message_to_reply_to.reply(message_text)
        await interaction.send("Done!", ephemeral=True)
    else:
        await channel_to_send_to.send(message_text)
        await interaction.send("Done!", ephemeral=True)


@bot.slash_command(description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.send("Pong!")


@bot.slash_command(description="Get a random joke")
async def joke(interaction: discord.Interaction):
    await interaction.response.defer()
    req = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
    jsonobj = req.json()
    joke = jsonobj['joke']
    await interaction.send(joke)


# Wiki Page

subreddits = {"Languages": {

    "First Language English": "https://www.reddit.com/r/igcse/wiki/group1-languages/first-language-english",
    "Hindi as a Second Language": "https://www.reddit.com/r/igcse/wiki/group1-languages/hindi",
    "French": "https://www.reddit.com/r/igcse/wiki/group1-languages/french",
    "English Literature": "https://www.reddit.com/r/igcse/wiki/group1-languages/english-literature",
    "Mandarin, ESL, Malay, Spanish, German": "https://www.reddit.com/r/igcse/wiki/group1-languages",
    "Other Languages": "https://www.reddit.com/r/igcse/wiki/group1-languages"

},

    "Humanities": {

        "Economics": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/economics",
        "Environmental Management": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/evm",
        "Geography": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/geography",
        "Global Perspectives, Pakistan Studies and Sociology": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci",
        "History": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/history",
        "Islamiyat": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/islamiyat"

    },

    "Sciences": {

        "Physics": "https://www.reddit.com/r/igcse/wiki/group3-sciences/physics",
        "Chemistry": "https://www.reddit.com/r/igcse/wiki/group3-sciences/chemistry",
        "Biology": "https://www.reddit.com/r/igcse/wiki/group3-sciences/biology",
        "Combined/Co-ordinated Sciences": "https://www.reddit.com/r/igcse/wiki/group3-sciences/combined-co-sci",
        "Environmental Management": "https://www.reddit.com/r/igcse/wiki/group2-humanities-socsci/evm",
        "Physical Education": "https://www.reddit.com/r/igcse/wiki/group3-sciences"

    },

    "Mathematics": {

        "Maths:": "https://www.reddit.com/r/igcse/wiki/group4-maths/mathematics",
        "Additional Maths:": "https://www.reddit.com/r/igcse/wiki/group4-maths/additional-maths",
        "A-Level Maths": "https://www.reddit.com/r/igcse/wiki/group4-maths"

    },

    "Creative and Professional": {

        "Accounting": "https://www.reddit.com/r/igcse/wiki/group5-professional-creative/accounting",
        "Art and Design, Travel and Tourism and Food and Nutrition": "https://www.reddit.com/r/igcse/wiki/group5-professional-creative",
        "Business Studies": "https://www.reddit.com/r/igcse/wiki/group5-professional-creative/business-studies",
        "Computer Science": "https://www.reddit.com/r/igcse/wiki/group5-professional-creative/computer-science",
        "ICT": "https://www.reddit.com/r/igcse/wiki/group5-professional-creative/ict"

    }

}


class Groups(discord.ui.Select):
    def __init__(self):
        options = []
        for group in subreddits.keys():
            options.append(discord.SelectOption(label=group))
        super().__init__(
            placeholder="Choose a subject group...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        group = self.values[0]
        view = discord.ui.View(timeout=None)
        for subject in subreddits[group].keys():
            view.add_item(
                discord.ui.Button(label=subject, style=discord.ButtonStyle.url, url=subreddits[group][subject]))
        await interaction.response.edit_message(view=view)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Groups())


@bot.slash_command(description="View the r/igcse wiki page", guild_ids=[GUILD_ID])
async def wiki(interaction: discord.Interaction):
    await interaction.send(view=DropdownView())


# Search past papers

@bot.slash_command(description="Search for IGCSE past papers with subject code/question text")
async def search(interaction: discord.Interaction,
                 query: str = discord.SlashOption(name="query", description="Search query", required=True)):
    await interaction.response.defer(ephemeral=True)
    try:
        response = requests.get(f"https://paper.sc/search/?as=json&query={query}").json()
        if len(response['list']) == 0:
            await interaction.send("No results found in past papers. Try changing your query for better results.",
                                   ephemeral=True)
        else:
            embed = discord.Embed(title="Potential Match",
                                  description="Your question matched a past paper question!",
                                  colour=discord.Colour.green())
            for n, item in enumerate(response['list'][:3]):
                # embed.add_field(name="Result No.", value=str(n+1), inline=False)
                embed.add_field(name="Subject", value=item['doc']['subject'], inline=True)
                embed.add_field(name="Paper", value=item['doc']['paper'], inline=True)
                embed.add_field(name="Session", value=item['doc']['time'], inline=True)
                embed.add_field(name="Variant", value=item['doc']['variant'], inline=True)
                embed.add_field(name="QP Link", value=f"https://paper.sc/doc/{item['doc']['_id']}", inline=True)
                embed.add_field(name="MS Link", value=f"https://paper.sc/doc/{item['related'][0]['_id']}",
                                inline=True)
            await interaction.send(embed=embed, ephemeral=True)
    except:
        await interaction.send("No results found in past papers. Try changing your query for better results.",
                               ephemeral=True)


# Moderation Actions

class GuildPreferencesDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.pref = self.db.guild_preferences

    def set_pref(self, pref: str, pref_value, guild_id: int):
        """ 'pref' can be 'modlog_channel' or 'rep_enabled'. """
        if self.pref.find_one({"guild_id": guild_id}):
            result = self.pref.update_one({"guild_id": guild_id}, {"$set": {pref: pref_value}})
        else:
            result = self.pref.insert_one({"guild_id": guild_id, pref: pref_value})
        return result

    def get_pref(self, pref: str, guild_id: int):
        result = self.pref.find_one({"guild_id": guild_id})
        if result is None:
            return None
        else:
            return result.get(pref, None)


gpdb = GuildPreferencesDB(LINK)


@bot.slash_command(description="Set server preferences (for mods)")
async def set_preferences(interaction: discord.Interaction,
                          modlog_channel: discord.abc.GuildChannel = discord.SlashOption(name="modlog_channel",
                                                                                         description="Channel for log of timeouts, bans, etc.",
                                                                                         required=False),
                          rep_enabled: bool = discord.SlashOption(name="rep_enabled",
                                                                  description="Enable the reputation system?",
                                                                  required=False),
                          suggestions_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="suggestions_channel",
                              description="Channel for new server suggestions to be displayed and voted upon.",
                              required=False),
                          warnlog_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="warnlog_channel",
                              description="Channel for warns to be logged.",
                              required=False)):
    if not await isModerator(interaction.user):
        await interaction.send("You are not authorized to perform this action", ephemeral=True)
        return
    await interaction.response.defer()
    if modlog_channel:
        gpdb.set_pref('modlog_channel', modlog_channel.id, interaction.guild.id)
    if rep_enabled:
        gpdb.set_pref('rep_enabled', rep_enabled, interaction.guild.id)
    if suggestions_channel:
        gpdb.set_pref("suggestions_channel", suggestions_channel.id, interaction.guild.id)
    if warnlog_channel:
        gpdb.set_pref("warnlog_channel", warnlog_channel.id, interaction.guild.id)
    await interaction.send("Done.")


@bot.slash_command(description="Warn a user (for mods)")
async def warn(interaction: discord.Interaction,
               user: discord.Member = discord.SlashOption(name="user", description="User to warn",
                                                          required=True),
               reason: str = discord.SlashOption(name="reason", description="Reason for warn", required=True)):
    action_type = "Warn"
    mod = interaction.user
    if not await isModerator(mod):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    warnlog_channel = gpdb.get_pref("warnlog_channel", interaction.guild.id)
    if warnlog_channel:
        ban_msg_channel = bot.get_channel(warnlog_channel)
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await interaction.send(f"{user.name}#{user.discriminator} has been warned.")
        await ban_msg_channel.send(ban_msg)
    channel = await user.create_dm()
    await channel.send(
        f"You have been warned in r/IGCSE by moderator {mod} for \"{reason}\".\n\nPlease be mindful in your further interaction in the server to avoid further action being taken against you, such as a timeout or a ban.")


@bot.slash_command(description="Timeout a user (for mods)")
async def timeout(interaction: discord.Interaction,
                  user: discord.Member = discord.SlashOption(name="user", description="User to timeout",
                                                             required=True),
                  time_: str = discord.SlashOption(name="duration",
                                                   description="Duration of timeout (e.g. 1d5h) up to 28 days (use 'permanent')",
                                                   required=True),
                  reason: str = discord.SlashOption(name="reason", description="Reason for timeout", required=True)):
    action_type = "Timeout"
    mod = interaction.user.mention
    if not await isModerator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    if time_.lower() == "unspecified" or time_.lower() == "permanent" or time_.lower() == "undecided":
        seconds = 86400 * 28
    else:
        seconds = 0
        if "d" in time_:
            seconds += int(time_.split("d")[0]) * 86400
            time_ = time_.split("d")[1]
        if "h" in time_:
            seconds += int(time_.split("h")[0]) * 3600
            time_ = time_.split("h")[1]
        if "m" in time_:
            seconds += int(time_.split("m")[0]) * 60
            time_ = time_.split("m")[1]
        if "s" in time_:
            seconds += int(time_.split("s")[0])
    if seconds == 0:
        await interaction.send("You can't timeout for zero seconds!", ephemeral=True)
        return
    await user.edit(timeout=discord.utils.utcnow() + datetime.timedelta(seconds=seconds))
    human_readable_time = f"{seconds // 86400}d {(seconds % 86400) // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s"
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)"""
        await ban_msg_channel.send(ban_msg)
    await interaction.send(
        f"{user.name}#{user.discriminator} has been put on time out until <t:{int(time.time()) + seconds}>, which is <t:{int(time.time()) + seconds}:R>.")


@bot.slash_command(description="Untimeout a user (for mods)")
async def untimeout(interaction: discord.Interaction,
                    user: discord.Member = discord.SlashOption(name="user", description="User to untimeout",
                                                               required=True)):
    action_type = "Remove Timeout"
    mod = interaction.user.mention
    if not await isModerator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await user.edit(timeout=None)
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.send(f"Timeout has been removed from {user.name}#{user.discriminator}.")


@bot.slash_command(description="Ban a user from the server (for mods)")
async def ban(interaction: discord.Interaction,
              user: discord.User = discord.SlashOption(name="user", description="User to ban",
                                                       required=True),
              reason: str = discord.SlashOption(name="reason", description="Reason for ban", required=True)):
    action_type = "Ban"
    mod = interaction.user.mention
    if not await isModerator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    try:
        if interaction.guild.id == 576460042774118420:  # r/igcse
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'. If you feel this ban was done in error, to appeal your ban, please fill the form below.\nhttps://forms.gle/8qnWpSFbLDLdntdt8")
        else:
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.ban(user, delete_message_days=1)
    await interaction.send(f"{user.name}#{user.discriminator} has been banned.")


@bot.slash_command(description="Unban a user from the server (for mods)")
async def unban(interaction: discord.Interaction,
                user: str = discord.SlashOption(name="user_id", description="Id of the user to unban",
                                                required=True)):
    action_type = "Unban"
    mod = interaction.user.mention
    if not await isModerator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    bans = await interaction.guild.bans()
    for ban in bans:
        if ban.user.id == int(user):
            await interaction.guild.unban(ban.user)
            await interaction.channel.send(f"{ban.user.name}#{ban.user.discriminator} has been unbanned.")

            ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
            if ban_msg_channel:
                try:
                    last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
                    case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
                except:
                    case_no = 1
                ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {ban.user.name}#{ban.user.discriminator} ({ban.user.id})
Moderator: {mod}"""
                await ban_msg_channel.send(ban_msg)
            return


@bot.slash_command(description="Kick a user from the server (for mods)")
async def kick(interaction: discord.Interaction,
               user: discord.User = discord.SlashOption(name="user", description="User to kick",
                                                        required=True),
               reason: str = discord.SlashOption(name="reason", description="Reason for kick", required=True)):
    action_type = "Kick"
    mod = interaction.user.mention
    if not await isModerator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    try:
        await user.send(
            f"Hi there from {interaction.guild.name}. You have been kicked from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.kick(user)
    await interaction.send(f"{user.name}#{user.discriminator} has been kicked.")


# Study Sessions

study_roles = {
    576463745073807372: 941505928988078141,
    576463729802346516: 943360807352287364,
    576463717844254731: 942792081808699472,
    576461721900679177: 941506098928689172,
    579288532942848000: 943360586731905024,
    579292149678342177: 945567738452135956,
    576464244455899136: 941504697980825621,
    576463493646123025: 945568090895294564,
    576463562084581378: 941224721100460082,
    576463593562701845: 941219105808187402,
    579386214218465281: 945569646436843530,
    576463609325158441: 945562595912474654,
    576463682054389791: 945569438571307019,
    576461701332074517: 941224259018166322,
    576463472544710679: 945562270832922644,
    871702123505655849: 941224492125011978,
    576463638983082005: 941218859250225152,
    868056343871901696: 941504895700320266,
    929349933432193085: 941218932570869770,
    576463799582851093: 944761951064567819,
    576463769526599681: 942795887946633268,
    576463668808646697: 945561426305630240,
    576464116336689163: 942794982333513738,
    576463907485646858: 945568732393140224,
    871589653315190845: 942791804464541726,
    576463811327033380: 942791457104855041,
    576463820575211560: 945565232032542802,
    576463893858222110: 945565876764155934,
    576463832168398852: 945568301860413501,
    871590306338971678: 945568902396661770,
    886883608504197130: 945567198603280424,
    576464270041022467: 945569054335303710,
}


@bot.slash_command(description="Start a study session", guild_ids=[GUILD_ID])
async def study_session(interaction: discord.Interaction):
    try:
        role = interaction.guild.get_role(study_roles[interaction.channel.id])
    except:
        await interaction.send(
            "Please use this command in the subject channel of the subject you're starting a study session for.",
            ephemeral=True)
        return
    study_sesh_channel = bot.get_channel(941276796937179157)
    msg_history = await study_sesh_channel.history(limit=3).flatten()
    for msg in msg_history:
        if (str(interaction.user.mention) in msg.content or str(role.mention) in msg.content) and \
                (msg.created_at.replace(tzinfo=None) + datetime.timedelta(minutes=60) > datetime.datetime.utcnow()):
            await interaction.send(
                "Please wait until one hour after your previous ping or after a study session in the same subject to start a new study session.",
                ephemeral=True)
            return
    voice_channel = interaction.user.voice
    if voice_channel is None:
        await interaction.send("You must be in a voice channel to use this command.", ephemeral=True)
    else:
        await study_sesh_channel.send(
            f"{role.mention} - Requested by {interaction.user.mention} - Please join {voice_channel.channel.mention}")
        await interaction.send(
            f"Started a {role.name.lower().replace(' study ping', '').title()} study session at {voice_channel.channel.mention}.")
        await voice_channel.channel.edit(
            name=f"{role.name.lower().replace(' study ping', '').title()} Study Session")


bot.run(TOKEN)
