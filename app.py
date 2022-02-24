import os
import datetime
import requests
import time
import operator
import traceback
import nextcord as discord

# Set up Discord API Token and KVStore API Key in a .env file and use the command "heroku local" to run the bot locally.

TOKEN = os.environ.get("IGCSEBOT_TOKEN")
API_KEY = os.environ.get("KVSTORE_API_KEY")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

async def refreshKeywords():
    global keywords
    channel = client.get_channel(929910420326727730)
    messages = await channel.history(limit=500).flatten()
    keywords = {message.content.splitlines()[0].lower() : "\n".join(message.content.splitlines()[1:]) for message in messages}

async def refreshReactionRoles():
    global reactionroles
    channel = client.get_channel(932454877915910144)
    messages = await channel.history(limit=500).flatten()
    reactionroles = {int(message.content.splitlines()[0]) : {i.split()[0]: int(i.split()[1]) for i in message.content.splitlines()[1:]} for message in messages}
    return reactionroles

async def getLeaderboard():
    channel = client.get_channel(862171720965029898)
    try:
        message = await channel.history(limit=1).flatten()
        return message[0], {message[0].guild.get_member(int(line.split(" - ")[0].replace("<@","").replace(">","").replace("!",""))) : int(line.split(" - ")[1]) for line in message[0].content.splitlines()[1:]}
    except:
        message = await channel.send("**REP LEADERBOARD**")
        return message, dict()

async def removeUser(userid):
    req = requests.delete(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    return True

async def getRepNew(userid):
    req = requests.get(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    return int(req.json().get("value","0"))

async def addRepNew(userid):
    rep = await getRepNew(userid)
    req = requests.put(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY}, data=str(rep+1))
    return rep+1

async def changeRepNew(userid, rep):
    req = requests.put(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY}, data=str(rep))
    return True

async def getLeaderboardNew(offset=0):
    req = requests.get(f"https://api.kvstore.io/collections/rep_leaderboard/items?offset={offset}&limit=100", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    leaderboard = {}
    for item in req.json():
        leaderboard[int(item['key'])] = int(item['value'])
    if len(leaderboard) == 100:
        leaderboard = {**leaderboard, **(await getLeaderboardNew(offset+100))}
    return {k: v for k, v in sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)} # Descending sort by rep

async def addRep(user):
    message, leaderboard = await getLeaderboard()
    try:
        current_rep = leaderboard[user]
    except:
        current_rep = 0
    leaderboard[user] = current_rep + 1
    leaderboard = dict(sorted(leaderboard.items(), key=operator.itemgetter(1),reverse=True))
    new_leaderboard = "**REP LEADERBOARD**"
    for user,rep in leaderboard.items():
        try:
            if rep > 0:
                new_leaderboard += f"\n{user.mention} - {rep}"
        except:
            pass
    await message.edit(content=new_leaderboard)
    backup_channel= client.get_channel(869753809428160602)
    backup = await backup_channel.send(".")
    await backup.edit(content=new_leaderboard)
    members = list(leaderboard.keys())[:3]
    role = discord.utils.get(member.guild.roles, name="Reputed")
    for m in role.members:
            await m.remove_roles(role)
    for member in members:
        await member.add_roles(role)
    return current_rep + 1

async def changeRep(user, new_rep):
    message, leaderboard = await getLeaderboard()
    leaderboard[user] = new_rep
    leaderboard = dict(sorted(leaderboard.items(), key=operator.itemgetter(1),reverse=True))
    new_leaderboard = "**REP LEADERBOARD**"
    for user,rep in leaderboard.items():
        try:
            if rep > 0:
                new_leaderboard += f"\n{user.mention} - {rep}"
        except:
            pass
    await message.edit(content=new_leaderboard)
    backup_channel= client.get_channel(869753809428160602)
    backup = await backup_channel.send(".")
    await backup.edit(content=new_leaderboard)
    members = list(leaderboard.keys())[:3]
    role = discord.utils.get(member.guild.roles, name="Reputed")
    for m in role.members:
        await m.remove_roles(role)
    for member in members:
        await member.add_roles(role)

async def lowLikelihood(message):
    role = discord.utils.get(message.guild.roles, name="Discord Mod")
    await message.reply(f"My automatic evaluation has returned that the likelihood of the message being spam is low. Please wait for {role.mention} to review the message.")

async def spamMessage(message, reporter):
    user = message.author
    bot = message.guild.get_member(861445044790886467)
    mod_role = discord.utils.get(message.guild.roles, id=578170681670369290)
    await message.reply(f"{message.author.mention} has been muted for sending scam messages. (Reported by {reporter.mention})\nIf this action was done in error, {mod_role.mention} will review the mute and revoke it if necessary")
    ban_msg_channel = client.get_channel(690267603570393219)
    last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
    role = discord.utils.get(message.guild.roles, id=787670627967959087)
    await user.add_roles(role)
    case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1 # Increment previous case number
    ban_msg = f"""Case #{case_no} | [Mute]
Username: {user.name}#{user.discriminator} ({user.id})
Reporter: {reporter.mention}
Reason: Spamming messages in channels"""
    await ban_msg_channel.send(ban_msg)
    log_channel = client.get_channel(792775200394575882)
    await log_channel.send(content=f"Reporter: {reporter.mention}\n\nTranscript of message sent by {user.mention}:\n\n{message.content}")

    for channel in message.guild.text_channels: # Delete any other instances of the spam message sent
        fetchMessage = await channel.history(limit=10).flatten()
        if fetchMessage:
            for m in fetchMessage:
                if m.content == message.content:
                    try:
                        await m.delete()
                    except:
                        pass

helper_roles = {
    576463745073807372 : 696688133844238367,
    576463729802346516 : 696415409720786994,
    576463717844254731 : 696415478331211806,
    576461721900679177 : 697031993820446720,
    576463988506886166 : 697032184451563530,
    579288532942848000 : 854000279933812737,
    579292149678342177 : 697032265624060005,
    576464244455899136 : 863699698234032168,
    576463493646123025 : 697031812102225961,
    576463562084581378 : 697031148685230191,
    576463593562701845 : 697090437520949288,
    579386214218465281 : 888382475645120575,
    576463609325158441 : 776986644757610517,
    576463682054389791 : 697031853369983006,
    576461701332074517 : 697030773814853633,
    576463472544710679 : 697030911023120455,
    871702123505655849 : 871702647223255050,
    576463638983082005 : 697031447021748234,
    868056343871901696 : 697031555457220673,
    576463799582851093 : 697031087985262612,
    576463769526599681 : 697030991205892156,
    576463668808646697 : 697407528685797417,
    576464116336689163 : 697031043089170463,
    576463907485646858 : 697031773435068466,
    871589653315190845 : 848529485351223325,
    576463811327033380 : 697031605100740698,
    576463820575211560 : 697031649233338408,
    576463893858222110 : 697031735086546954,
    576463832168398852 : 697031692115771513, 
    871590306338971678 : 871588409032990770,
    886883608504197130 : 886884656845312020,
    576464270041022467 : 863691773628907560,
    697072778553065542 : 578170681670369290,
    929349933432193085 : 929422215940825088,
}

study_roles = {
    576463745073807372 : 941505928988078141,
    576463729802346516 : 943360807352287364,
    576463717844254731 : 942792081808699472,
    576461721900679177 : 941506098928689172,
    579288532942848000 : 943360586731905024,
    579292149678342177 : 945567738452135956,
    576464244455899136 : 941504697980825621,
    576463493646123025 : 945568090895294564,
    576463562084581378 : 941224721100460082,
    576463593562701845 : 941219105808187402,
    579386214218465281 : 945569646436843530,
    576463609325158441 : 945562595912474654,
    576463682054389791 : 945569438571307019,
    576461701332074517 : 941224259018166322,
    576463472544710679 : 945562270832922644,
    871702123505655849 : 941224492125011978,
    576463638983082005 : 941218859250225152,
    868056343871901696 : 941504895700320266,
    929349933432193085 : 941218932570869770,
    576463799582851093 : 944761951064567819,
    576463769526599681 : 942795887946633268,
    576463668808646697 : 945561426305630240,
    576464116336689163 : 942794982333513738,
    576463907485646858 : 945568732393140224,
    871589653315190845 : 942791804464541726,
    576463811327033380 : 942791457104855041,
    576463820575211560 : 945565232032542802,
    576463893858222110 : 945565876764155934,
    576463832168398852 : 945568301860413501,
    871590306338971678 : 945568902396661770,
    886883608504197130 : 945567198603280424,
    576464270041022467 : 945569054335303710,
}

text_prompts = {"version" : "v2.0"}

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="Flynn#5627"))
    await refreshKeywords()
    await refreshReactionRoles()

@client.event
async def on_thread_join(thread):
    await thread.join() # Join all threads automatically

@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    pins = await channel.pins()
    chnl = client.get_channel(896390991857213511) # Pins channel for uploading to the subreddit wiki
    await chnl.send(f"New pin by {pins[0].author} in {channel.mention}: {pins[0].jump_url}")

@client.event
async def on_member_join(member):
    welcome_message = """Hello and welcome to the r/IGCSE official partnered server, a place where you can ask any doubts about your exams and find help in a topic you're struggling! We strongly suggest you read the following message to better know how our server works!

**How the server works?**
The server mostly entirely consists of the students who are doing their IGCSE and those who have already done their IGCSE. This server is a place where you can clarify any of your doubts regarding how exams work as well as any sort of help regarding a subject or a topic in which you struggle. Do be reminded that academic dishonesty is not allowed in this server and you may face consequences if found to be doing so. (Examples of academic dishonesty: Asking people to do your homework for you, sharing any leaked papers before the exam session has ended, etc.) Furthermore, we would like to remind you that posting pirated content like whole textbooks are not allowed in this server.

**How to ask for help?**
We have subject helpers for every subject to clear any doubts you may have. If you want a helper to entertain a doubt, you should say "helper". A timer of 15 minutes will start before the respective subject helper will be pinged. You will be reminded 3 minutes before the time elapses to cancel the ping if your doubt has been entertained. Remember to cancel your ping once a helper is helping you!

**How to contact the moderators?**
You can contact us by sending a message through @r/IGCSE Bot where it will be forwarded to the moderators to view. Do be reminded that only general server inquiries should be sent. Other inquiries like subject help will not be entertained as there are subject channels for that."""
    channel = await member.create_dm()
    desc = f"""Before joining our server, **we require all new users to pick up session roles**. These make sure that you will have access to the appropriate general chat channels and for our helpers to give you more specific advice.
**React to the corresponding reactions in {member.guild.get_channel(932550807755304990).mention} to verify and gain access to the rest of the server.**
Afterwards, react to the corresponding roles in {member.guild.get_channel(932570912660791346).mention} or {member.guild.get_channel(932546951055032330).mention} to gain access to your corresponding subject channels."""
    embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green())
    try:
        msg = await channel.send(welcome_message, embed=embedVar)
    except:
        pass
    channel = member.guild.get_channel(930088940654956575)
    embed = discord.Embed.from_dict(eval("""{'color': 15844367, 'type': 'rich', 'description': 'To verify, head to <#932550807755304990> to pick up your corresponding session role. This will grant you access to the rest of the server.\\n\\nNext, head to <#932570912660791346> or <#932546951055032330> to pick up subject roles for the subjects you are taking. These are essential if you wish to make use of the server, and if you wish to ask subject related queries. \\n\\nIf you have any issues do DM <@!861445044790886467> and we will help you out.\\n\\nYou may read our <#576460042774118422> and type `help` in <#669286559404785665> to learn more about our server and about <@!861445044790886467> \\n\\n**NOTE: If you do not verify you will not be able to access the server.**', 'title': 'Welcome to the server!'}"""))
    await channel.send(content=member.mention, embed=embed)
    
@client.event
async def on_raw_reaction_add(reaction):
    chnl = await client.fetch_channel(reaction.channel_id)
    msg = await chnl.fetch_message(reaction.message_id)

    try: # Reaction Roles
        items = reactionroles[reaction.message_id]
        roleid = items[reaction.emoji.name]
        role = msg.guild.get_role(roleid)
        await reaction.member.add_roles(role)
    except:
        pass

    if reaction.channel_id == 932550807755304990: # Verification if session role is picked up.
        verified = discord.utils.get(reaction.member.guild.roles, name="Verified")
        if verified not in reaction.member.roles:
            await reaction.member.add_roles(role, verified)

    if reaction.channel_id == 930274101321400361 and str(reaction.emoji) == "🔒": # Emote suggestion channel - Finalise button clicked
        author = msg.channel.guild.get_member(reaction.user_id)
        roles = [role.name for role in author.roles]
        if (not ("Discord Mod" in roles or "Temp Mod" in roles)) or author == client.user: return
        upvotes = 0
        downvotes = 0
        for r in msg.reactions:
            if r.emoji == "👍":
                upvotes += r.count
            elif r.emoji == "👎":
                downvotes += r.count
        name = msg.content[msg.content.find(':')+1 : msg.content.find(':', msg.content.find(':')+1)]
        if upvotes/downvotes >= 3:
            emoji = await msg.guild.create_custom_emoji(name=name, image=requests.get(msg.attachments[0].url).content)
            await msg.reply(f"The submission by {msg.mentions[0]} for the emote {str(emoji)} has passed.")
        else:
            await msg.reply(f"The submission by {msg.mentions[0]} for the emote `:{name}:`has failed.")

    if not msg.guild and msg.author == client.user and "Firstly, how old are you?" in msg.embeds[0].description:  # Old DM Verification System
        guild = client.get_guild(576460042774118420)
        for r in msg.reactions:
            users = [user async for user in r.users() if user != client.user]
            if users:
                member = guild.get_member(users[0].id)
                break
        channel = await member.create_dm()
        if str(reaction.emoji) == "1️⃣":
            await channel.send("You are under 13 years old. You will not be given access to the server as you are not yet eligible to join as per Discord TOS.")
        elif str(reaction.emoji) == "2️⃣":
            desc = """2. Are you planning to take IGCSE?
React with one of the following
1️⃣ – Yes
2️⃣ – No"""
            embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green())
            m = await channel.send(embed=embedVar)
            await m.add_reaction('1️⃣')
            await m.add_reaction('2️⃣')

    if not msg.guild and msg.author == client.user and "2. Are you planning to take IGCSE?" in msg.embeds[0].description:  # Old DM Verification System
        guild = client.get_guild(576460042774118420)
        for r in msg.reactions:
            users = [user async for user in r.users() if user != client.user]
            if users:
                member = guild.get_member(users[0].id)
                break
        channel = await member.create_dm()
        if str(reaction.emoji) == "1️⃣":
            desc = """3. When do you plan to take IGCSE?
React with one of the following
1️⃣ – March 2022
2️⃣ – June 2022
3️⃣ – November 2022
4️⃣ – March 2023
5️⃣ – June 2023
6️⃣ – October 2023"""
            embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green()) 
            m = await channel.send(embed=embedVar)
            await m.add_reaction('1️⃣')
            await m.add_reaction('2️⃣')
            await m.add_reaction('3️⃣')
            await m.add_reaction('4️⃣')
            await m.add_reaction('5️⃣')
            await m.add_reaction('6️⃣')
        elif str(reaction.emoji) == "2️⃣":
            guild = client.get_guild(576460042774118420)
            role = discord.utils.get(guild.roles, name="NOT IGCSE")
            verified = discord.utils.get(guild.roles, name="Verified")
            await member.add_roles(role, verified)
            await member.send("Thank you for answering the questions. You may now access the server.")

    if not msg.guild and msg.author == client.user and "3. When do you plan to take IGCSE?" in msg.embeds[0].description: # Old DM Verification System
        guild = client.get_guild(576460042774118420)
        for r in msg.reactions:
            users = [user async for user in r.users() if user != client.user]
            if users:
                member = guild.get_member(users[0].id)
                break
        channel = await member.create_dm()
        
        for r in msg.reactions:
            if r.count == 2:
                if str(reaction.emoji) == "1️⃣":
                    role = discord.utils.get(guild.roles, name="F/M 2022")
                elif str(reaction.emoji) == "2️⃣":
                    role = discord.utils.get(guild.roles, name="M/J 2022")
                elif str(reaction.emoji) == "3️⃣":
                    role = discord.utils.get(guild.roles, name="O/N 2022")
                elif str(reaction.emoji) == "4️⃣":
                    role = discord.utils.get(guild.roles, name="F/M 2023")
                elif str(reaction.emoji) == "5️⃣":
                    role = discord.utils.get(guild.roles, name="M/J 2023")
                elif str(reaction.emoji) == "6️⃣":
                    role = discord.utils.get(guild.roles, name="O/N 2023")
                
                verified = discord.utils.get(guild.roles, name="Verified")
                if verified in member.roles:
                    if role not in member.roles:
                        await member.add_roles(role)
                else:
                    await member.add_roles(role, verified)
                    await member.send("Thank you for answering the questions. You may now access the server.")
    
    if msg.guild and msg.author == client.user and "Firstly, how old are you?" in msg.embeds[0].description: # Old Server Verification System
        guild = msg.guild
        member = reaction.member
        channel = msg.channel
        if str(reaction.emoji) == "1️⃣":
            m = await channel.send(f"{member.mention}, you are under 13 years old. You will not be given access to the server as you are not yet eligible to join as per Discord TOS.", delete_after=10.0)

    if msg.guild and msg.author == client.user and "2. Are you planning to take IGCSE?" in msg.embeds[0].description: # Old Server Verification System
        guild = msg.guild
        member = reaction.member
        channel = msg.channel
        if str(reaction.emoji) == "2️⃣":
            role = discord.utils.get(guild.roles, name="NOT IGCSE")
            verified = discord.utils.get(guild.roles, name="Verified")
            await member.add_roles(role, verified)
            channel = member.guild.get_channel(920138547858645072)
            perms = channel.overwrites_for(member)
            perms.read_messages, perms.view_channel, perms.read_message_history, perms.add_reactions = False, False, False, False
            await channel.set_permissions(member, overwrite=perms)
            await channel.send(f"{member.mention}, Thank you for answering the questions. You may now access the server.", delete_after=10.0)

    if msg.guild and msg.author == client.user and "3. When do you plan to take IGCSE?" in msg.embeds[0].description: # Old Server Verification System
        guild = msg.guild
        member = reaction.member
        channel = msg.channel
        
        if str(reaction.emoji) == "1️⃣":
            role = discord.utils.get(guild.roles, name="F/M 2022")
        elif str(reaction.emoji) == "2️⃣":
            role = discord.utils.get(guild.roles, name="M/J 2022")
        elif str(reaction.emoji) == "3️⃣":
            role = discord.utils.get(guild.roles, name="O/N 2022")
        elif str(reaction.emoji) == "4️⃣":
            role = discord.utils.get(guild.roles, name="F/M 2023")
        elif str(reaction.emoji) == "5️⃣":
            role = discord.utils.get(guild.roles, name="M/J 2023")
        elif str(reaction.emoji) == "6️⃣":
            role = discord.utils.get(guild.roles, name="O/N 2023")
        
        verified = discord.utils.get(guild.roles, name="Verified")
        if verified in member.roles:
            if role not in member.roles:
                await member.add_roles(role)
        else:
            await member.add_roles(role, verified)
            channel = member.guild.get_channel(920138547858645072)
            perms = channel.overwrites_for(member)
            perms.read_messages, perms.view_channel, perms.read_message_history, perms.add_reactions = False, False, False, False
            await channel.set_permissions(member, overwrite=perms)
            await channel.send(f"{member.mention}, thank you for answering the questions. You may now access the server.", delete_after=10.0)
    
    if not msg.guild and str(reaction.emoji) == '✅': # Old DM Suggestion system
        channel = client.get_channel(758562162616303658)
        author = channel.guild.get_member(reaction.user_id)
        if not author.bot:
            embedVar = discord.Embed(title=f"Suggestion by {author}", description=f"Total Votes: 0\n\n{'🟩'*10}\n\nSuggestion: {msg.clean_content}", colour = discord.Colour.green())
            msg1 = await channel.send(embed=embedVar)
            await chnl.send("Your suggestion has been noted! Thank you!")
            await msg1.add_reaction('✅')
            await msg1.add_reaction('❌')

    if str(reaction.emoji) == "🟢" and reaction.user_id != 861445044790886467 and msg.channel.id == 758562162616303658: # Suggestion accepted by mod in #suggestions-voting
        author = msg.channel.guild.get_member(reaction.user_id)
        roles = [role.name.lower() for role in author.roles]
        if "discord mod" in roles:
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
            embed.add_field(name="Accepted ✅", value=f"This suggestion has been accepted by the moderators. ({author})", inline=False)
            await msg.edit(embed=embed)
            await msg.pin()
        return

    if str(reaction.emoji) == "🔴" and reaction.user_id != 861445044790886467 and msg.channel.id == 758562162616303658: # Suggestion rejected by mod in #suggestions-voting
        author = msg.channel.guild.get_member(reaction.user_id)
        roles = [role.name.lower() for role in author.roles]
        if "discord mod" in roles:
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
            embed.add_field(name="Rejected ❌", value=f"This suggestion has been rejected by the moderators. ({author})", inline=False)
            await msg.edit(embed=embed)
        return

    # Suggestion voting system
    vote = 0
    for reaction in msg.reactions:
        if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            async for user in reaction.users():
                if user == client.user:
                    vote += 1
                    break
    
    if vote == 2:
        for reaction in msg.reactions:
            if str(reaction.emoji) == "✅":
                yes = reaction.count - 1
            if str(reaction.emoji) == "❌":
                no = reaction.count - 1
        try:
            yes_p = round((yes / (yes+no)) * 100) // 10
            no_p = 10 - yes_p 
        except:
            yes_p = 10
            no_p = 0
        description = f"Total Votes: {yes+no}\n\n{yes_p*10}% {yes_p*'🟩'}{no_p*'🟥'} {no_p*10}%\n"
        description += "\n".join(msg.embeds[0].description.split("\n")[3:])
        embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
        for field in msg.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await msg.edit(embed=embed)

@client.event
async def on_raw_reaction_remove(reaction):

    channel = client.get_channel(reaction.channel_id)
    msg = await channel.fetch_message(reaction.message_id)

    try: # Reaction roles - remove role
        items = reactionroles[reaction.message_id]
        roleid = items[reaction.emoji.name]
        role = msg.guild.get_role(roleid)
        member = discord.utils.get(msg.guild.members, id=reaction.user_id)
        await member.remove_roles(role)
    except:
        pass

    vote = 0 # Suggestions voting system - remove vote
    for reaction in msg.reactions:
        if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            async for user in reaction.users():
                if user == client.user:
                    vote += 1
                    break
    
    if vote == 2:
        for reaction in msg.reactions:
            if str(reaction.emoji) == "✅":
                yes = reaction.count - 1
            if str(reaction.emoji) == "❌":
                no = reaction.count - 1
        try:
            yes_p = round((yes / (yes+no)) * 100) // 10
            no_p = 10 - yes_p 
        except:
            yes_p = 10
            no_p = 0
        description = f"Total Votes: {yes+no}\n\n{yes_p*10}% {yes_p*'🟩'}{no_p*'🟥'} {no_p*10}%\n"
        description += "\n".join(msg.embeds[0].description.split("\n")[3:])
        embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=description)
        for field in msg.embeds[0].fields:
            try:
                embed.add_field(name=field.name, value=field.value, inline=False)
            except:
                pass
        await msg.edit(embed=embed)


@client.event
async def on_message(message):
    try:
        global keywords
        if message.author == client.user:
            return

        if not message.guild: # If DM
            try:
                msg = await message.channel.fetch_message(message.reference.message_id)
                if "simply type your suggestion" in msg.content: # Old suggestion system
                    channel = client.get_channel(758562162616303658)
                    embedVar = discord.Embed(title=f"Suggestion by {message.author}", description=f"Total Votes: 0\n\n{'🟩'*10}\n\nSuggestion: {message.clean_content}", colour = discord.Colour.green())
                    msg1 = await channel.send(embed=embedVar)
                    await message.reply("Your suggestion has been noted! Thank you!")
                    await msg1.add_reaction('✅')
                    await msg1.add_reaction('❌')
            except:
                if "suggestion" in message.content.lower(): # Old suggestion system
                    await message.reply("Hi there! To submit a suggestion for the r/IGCSE Server, simply type your suggestion as a REPLY to this message.")
                else:
                    if message.content or message.attachments: # Receiving Modmails system
                        guild = client.get_guild(576460042774118420)
                        category = discord.utils.get(guild.categories, name='COMMS')
                        channel = discord.utils.get(category.channels, topic=str(message.author.id))
                        if not channel:
                            category = discord.utils.get(guild.categories, name='COMMS2')
                            channel = discord.utils.get(category.channels, topic=str(message.author.id))
                            if not channel:
                                category = discord.utils.get(guild.categories, name='COMMS3')
                                channel = discord.utils.get(category.channels, topic=str(message.author.id))
                                if not channel:
                                    try:
                                        channel = await guild.create_text_channel(str(message.author).replace("#","-"), category=category, topic=str(message.author.id))
                                    except:
                                        createdm_channel = client.get_channel(895961641219407923)
                                        await createdm_channel.send(f"The category COMMS3 has reached its capacity limit. Please delete some channels from COMMS2 to allow for new incoming messages.\n\nNew Message Received:\n{message.author} - {message.clean_content}")
                        embedVar = discord.Embed(title=f"Message Received", description=message.clean_content, colour = discord.Colour.green())
                        embedVar.add_field(name="Author", value=message.author, inline=True)
                        await channel.send(embed=embedVar)
                        for attachment in message.attachments:
                            await channel.send(file=await attachment.to_file())
                        await message.reply("Your message has been forwarded to our moderators! Any reply by the mods will be conveyed to you by DM.")
            return

        if message.channel.id == 895961641219407923: # Creating modmail channels in #create-dm
            member = message.guild.get_member(int(message.content))
            category = discord.utils.get(message.guild.categories, name='COMMS')
            channel = discord.utils.get(category.channels, topic=str(member.id))
            if not channel:
                category = discord.utils.get(message.guild.categories, name='COMMS2')
                channel = discord.utils.get(category.channels, topic=str(member.id))
                if not channel:
                    category = discord.utils.get(message.guild.categories, name='COMMS3')
                    channel = discord.utils.get(category.channels, topic=str(member.id))
                    if not channel:
                        category = discord.utils.get(message.guild.categories, name='COMMS3')
                        channel = await message.guild.create_text_channel(str(member).replace("#","-"), category=category, topic=str(member.id))
            await message.reply(f"DM Channel has been created at {channel.mention}")
            return
        
        if message.channel.category: # Sending modmails
            if (message.channel.category.name.lower() == "comms" or message.channel.category.name.lower() == "comms2" or message.channel.category.name.lower() == "comms3") and not message.author.bot:
                if int(message.channel.topic) == message.author.id:
                    embedVar = discord.Embed(title=f"Message Received", description=message.clean_content, colour = discord.Colour.green())
                    embedVar.add_field(name="Author", value=message.author, inline=True)
                    await message.channel.send(embed=embedVar)
                    await message.delete()
                else:
                    member = message.guild.get_member(int(message.channel.topic))
                    channel = await member.create_dm()
                    embedVar = discord.Embed(title=f"Message from r/IGCSE Moderators", description=message.clean_content, colour = discord.Colour.green())
                    embedVar.add_field(name="Author", value=message.author, inline=True)
                    
                    try:
                        await channel.send(embed=embedVar)
                        if not message.attachments:
                            await message.channel.send(embed=embedVar)
                            await message.delete()
                    except:
                        perms = message.channel.overwrites_for(member)
                        perms.send_messages, perms.read_messages, perms.view_channel, perms.read_message_history, perms.attach_files= True, True, True, True, True
                        await message.channel.set_permissions(member, overwrite=perms)
                        return
                            
                    for attachment in message.attachments:
                            embedVar.set_image(url=attachment.url)
                            try:
                                await channel.send(embed=embedVar)
                                await message.channel.send(embed=embedVar)
                            except:
                                await message.reply("Unfortunately, the user has their DMs turned off.")

        if len(message.content.split()):
            if message.content.split()[0].lower() == "help":
                if message.channel.id not in [669286559404785665, 932548192329957376]: # Not in a designated bot channel
                    msg = await message.reply(f"If you wish to use the help command, please use it in the {client.get_channel(669286559404785665).mention} channel.", delete_after=10.0)
                    return
                if len(message.content.split()) <= 2:
                    try:
                        p = int(message.content.split()[1]) - 1
                    except:
                        p = 0
                    pages = []
                    page = 1
                    help_pages = {(f"Keywords ({n+1})", "These are the keywords you can send in any channel to receive their corresponding autoreplies from r/IGCSE Bot") : i for n, i in enumerate([list(text_prompts.items())[x:x+16] for x in range(0, len(text_prompts), 16)])}
                    help_pages.update({(f"Keywords ({n+1+len(help_pages)})", "These are the keywords you can send in any channel to receive their corresponding autoreplies from r/IGCSE Bot") : i for n, i in enumerate([list(keywords.items())[x:x+16] for x in range(0, len(keywords), 16)])})
                    help_pages.update({("Reputation", "These are the commands associated with the Rep system on this server.") : [("Rep", "This command allows you to view the current reputation leaderboard."), ("My Rep", "This command allows you to view your current reputation score."), ("Thanks", "Say this while mentioning user(s) or replying to a message to give the mentioned user(s) a reputation point! Alternatives: thank you, thx, tysm, thank u, thnks, tanks, thanku, ty"), ("You're Welcome", "Say this while replying to a message to get a reputation point, in case the user has not thanked you. Alternatives: youre welcome, ur welcome, u r welcome, your welcome, welcome, no problem, np, yw")],
                                ("Asking for Help", "These commands are used to ask for help in the server.") : [("Helper", "Use this command in any subject channel to ping the helpers in that channel after 15 minutes."), ("Cancel", "If your question has been answered before the 15 minutes have passed, reply to the message saying 'cancel' to cancel the ping. The question asker, all helpers, and mods can do this.")],
                                ("Modmail", "These are instructions on how to send Modmails to the server moderators.") : [("DM r/IGCSE Bot", "DM r/IGCSE Bot (the topmost user on the members list) with all your queries. These messages will be forwarded to us and we will reply to you through the bot by DM as well. Please ensure that you have enabled DMs in your settings.")],
                                ("Suggestions", "These are instructions on how to create, vote on, and comment on suggestions") : [("vote", "Send a suggestion as a message in #botspam and reply to the message saying 'vote' to send it to #suggestions-voting for members to vote on"), ("Commenting on Suggestions", "Reply to a suggestion in #suggestions-voting to comment on it. Your comment will be added to the embed directly"), ("Voting on Suggestions", "Click one of the reactions (✅ or ❌) under the suggestion message in #suggestions-voting to vote for or against it.")],
                                ("Helpers", "These are commands that only helpers can use.") : [("Pin", "Reply to any message saying 'pin' to pin it in the channel."), ("Unpin", "Reply to any message saying 'unpin' to unpin it from the channel.")],
                                ("Server Boosters", "These are commands that only server boosters can use.") : [("Color R G B", "Use this command, replacing R, G, and B with values between 0 and 255 (the RGB value) to get a custom color role that changes the color of your name in the server. For example, 'color 0 255 255'"), ("Color remove", "Removes your custom color role")],
                                ("Fun", "These are the commands you can send in any channel to have fun with r/IGCSE Bot") : [("Joke", "This command will send a random joke"), ("Ping", "Check the ping value of the connection to r/IGCSE Bot")],
                                ("Other", "These are miscellaneous commands programmed into r/IGCSE Bot") : [("Poll", "Reply to any message in any channel with 'poll' to create a poll in that channel (this is different from the suggestions feature)."), ("Help Command", "Use 'help n' where n is the page of the help pages you want to view. For example, 'help 5' will directly show you the 5th page of help."), ("Scam/Spam", "Reply either one of 'scam' or 'spam' to spam/scam messages sent in the server for r/IGCSE Bot to automatically evaluate it and mute the sender.")],
                                })

                    for title_desc, items in help_pages.items():
                        title, desc = title_desc
                        embedVar = discord.Embed(title=title, description=f"Page {page} of {len(help_pages)}\n\n{desc}", colour = discord.Colour.green())
                        for name, value in items:
                            embedVar.add_field(name=name, value=value, inline=False)
                        pages.append(embedVar)
                        page += 1

                    message = await message.reply(embed = pages[p])

                    await message.add_reaction('⏮')
                    await message.add_reaction('◀')
                    await message.add_reaction('🔒')
                    await message.add_reaction('▶')
                    await message.add_reaction('⏭')

                    i = p
                    reaction = None

                    while True:
                        if str(reaction) == '⏮':
                            i = 0
                            await message.edit(embed = pages[i])
                        elif str(reaction) == '◀':
                            if i > 0:
                                i -= 1
                                await message.edit(embed = pages[i])
                        elif str(reaction) == "🔒":
                            await message.clear_reactions()
                            return
                        elif str(reaction) == '▶':
                            if i < len(pages) - 1:
                                i += 1
                                await message.edit(embed = pages[i])
                        elif str(reaction) == '⏭':
                            i = len(pages) - 1
                            await message.edit(embed = pages[i])
                        
                        try:
                            reaction, user = await client.wait_for('reaction_add', timeout = 30.0)
                            if user == client.user:
                                reaction, user = await client.wait_for('reaction_add', timeout = 30.0)
                            await message.remove_reaction(reaction, user)
                        except:
                            break

                    await message.clear_reactions()

        if len(message.content.split()) > 0:
            if message.content.lower() == "colour remove" or message.content.lower() == "color remove": # Remove custom color role
                all_roles = await message.guild.fetch_roles()
                for role in all_roles:
                    if str(role.name) == str(message.author.id):
                        await message.author.remove_roles(role)
                        await message.reply("Your colour has been removed.")
                        return

            if "remove role" == message.content.lower()[:11] and len(message.content.split()) > 3:
                if message.author.id == 604335693757677588: # Only for Flynn
                    member = message.guild.get_member(int(message.content.split()[2]))
                    try:
                        role = discord.utils.get(message.guild.roles, id=int(message.content.split()[3]))
                    except:
                        role = None
                    if not role:
                        role = discord.utils.get(message.guild.roles, name=" ".join(message.content.split()[3:]))
                    await member.remove_roles(role)
                    await message.reply(f"Removed role {role.name} ({role.id}) from user {member}")

            if "give me role" == message.content.lower()[:12] and len(message.content.split()) > 3:
                if message.author.id == 604335693757677588: # Only for Flynn - Take a role
                    try:
                        role = discord.utils.get(message.guild.roles, id=int(message.content.split()[3]))
                    except:
                        role = None
                    if not role:
                        role = discord.utils.get(message.guild.roles, name=" ".join(message.content.split()[3:]))
                    await message.author.add_roles(role)
                    await message.reply(f"Gave you role {role.name} ({role.id})")

            if message.content.split()[0].lower() == "copy" and len(message.content.split()) == 3:
                if message.author.id == 604335693757677588: # Only for Flynn - Copy members from one role to another
                    role1 = discord.utils.get(message.guild.roles, id=int(message.content.split()[1]))
                    role2 = discord.utils.get(message.guild.roles, id=int(message.content.split()[2]))
                    count = 0
                    for member in role1.members:
                        await member.add_roles(role2)
                        count += 1
                    await message.reply(f"Copied {count} members from role {role1} to role {role2}.")

            if ".eval" == message.content.lower()[:5] and len(message.content.split()) > 1:
                if message.author.id == 604335693757677588: # Only for Flynn
                    try:
                        result = eval(" ".join(message.content.split()[1:]))
                    except:
                        result = f"Error: {traceback.format_exc()}"
                    await message.reply(f"```py\n{result}\n```")

            if ".await" == message.content.lower()[:6] and len(message.content.split()) > 1:
                if message.author.id == 604335693757677588: # Only for Flynn
                    try:
                        result = await eval(" ".join(message.content.split()[1:]))
                    except:
                        result = f"Error: {traceback.format_exc()}"
                    await message.reply(f"```py\n{result}\n```")

            if ".objectawait" == message.content.lower()[:12] and len(message.content.split()) > 1:
                if message.author.id == 604335693757677588: # Only for Flynn
                    try:
                        object = await eval(" ".join(message.content.splitlines()[0].split()[1:]))
                        result = await eval(" ".join(message.content.splitlines()[1]))
                    except:
                        result = f"Error: {traceback.format_exc()}"
                    await message.reply(f"```py\n{result}\n```")

            if ".object" == message.content.lower()[:7] and len(message.content.split()) > 1:
                if message.author.id == 604335693757677588: # Only for Flynn
                    try:
                        object = await eval(" ".join(message.content.splitlines()[0].split()[1:]))
                        result = eval(" ".join(message.content.splitlines()[1]))
                    except:
                        result = f"Error: {traceback.format_exc()}"
                    await message.reply(f"```py\n{result}\n```")

            if ".exec" == message.content.lower()[:5] and len(message.content.split()) > 1:
                if message.author.id == 604335693757677588: # Only for Flynn
                    try:
                        result = exec(" ".join(message.content.split()[1:]))
                    except:
                        result = f"Error: {traceback.format_exc()}"
                    await message.reply(f"```py\n{result}\n```")

            if message.content.split()[0].lower() == "colour" or message.content.split()[0].lower() == "color":
                roles = [role.name.lower() for role in message.author.roles]
                if "discord mod" in roles: # Give someone a color role
                    member = message.guild.get_member(int(message.content.split()[1]))
                    all_roles = await message.guild.fetch_roles()
                    num_roles = len(all_roles)
                    colour = message.content.split()[1]
                    if len(message.content.split()) == 5:
                        colour = discord.Color.from_rgb(int(message.content.split()[2]), int(message.content.split()[3]), int(message.content.split()[4]))
                    else:
                        await message.reply("Please use the command with the following format to change your role colour - ```[colour/color] [user_id] [red_value] [green_value] [blue_value]```\nFor example, ```color 255 0 0``` to get a fully red colour")
                        return
                    for role in all_roles:
                        if str(role.name) == str(member.id):
                            await role.edit(colour=colour)
                            break
                    else:
                        role = await message.guild.create_role(name=member.id, colour=colour)
                    await member.add_roles(role)
                    await role.edit(position=num_roles-16)
                    await message.reply(f"Added colour {colour} to user {member.mention}")
                elif "server booster" in roles: # Give yourself a color role
                    member = message.author
                    all_roles = await message.guild.fetch_roles()
                    num_roles = len(all_roles)
                    if len(message.content.split()) == 4:
                        colour = discord.Color.from_rgb(int(message.content.split()[1]), int(message.content.split()[2]), int(message.content.split()[3]))
                    else:
                        await message.reply("Please use the command with the following format to change your role colour - ```[colour/color] [user_id] [red_value] [green_value] [blue_value]```\nFor example, ```color 255 0 0``` to get a fully red colour")
                        return
                    for role in all_roles:
                        if str(role.name) == str(member.id):
                            await role.edit(colour=colour)
                            break
                    else:
                        role = await message.guild.create_role(name=member.id, colour=colour)
                    await member.add_roles(role)
                    await role.edit(position=num_roles-16)
                    await message.reply(f"Added colour {colour} to user {member.mention}")

        if message.content.lower() == "setup verify channel" and message.author.id == 604335693757677588: # Old server verification system
            await message.delete()

            desc = """Before joining our server, we require all new users to answer a few questions. These make sure that you will have access to the appropriate roles and subject channels.
    1. Firstly, how old are you?
    React with one of the following
    1️⃣ – Under 13
    2️⃣ – Over 13"""
            embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green())
            msg = await message.channel.send(embed=embedVar)
            await msg.add_reaction('1️⃣')
            await msg.add_reaction('2️⃣')

            desc = """2. Are you planning to take IGCSE?
    React with one of the following
    1️⃣ – Yes
    2️⃣ – No"""
            embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green())
            m = await message.channel.send(embed=embedVar)
            await m.add_reaction('1️⃣')
            await m.add_reaction('2️⃣')

            desc = """3. When do you plan to take IGCSE?
    React with one of the following
    1️⃣ – March 2022
    2️⃣ – June 2022
    3️⃣ – November 2022
    4️⃣ – March 2023
    5️⃣ – June 2023
    6️⃣ – October 2023"""
            embedVar = discord.Embed(title="Welcome to r/IGCSE!", description=desc, colour = discord.Colour.green())
            m = await message.channel.send(embed=embedVar)
            await m.add_reaction('1️⃣')
            await m.add_reaction('2️⃣')
            await m.add_reaction('3️⃣')
            await m.add_reaction('4️⃣')
            await m.add_reaction('5️⃣')
            await m.add_reaction('6️⃣')

        if message.content.lower() == "helper": # Helper ping system
            def check(msg):
                if msg.content.lower() == "cancel" and msg.channel == message.channel:
                    try: 
                        if msg.reference.message_id == message.id or msg.reference.message_id == m1.id:
                            roles = [role.name for role in msg.author.roles]
                            for role in roles:
                                if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower() or message.author == msg.author:
                                    return True
                        else:
                            if msg.reference.message_id == m4.id:
                                roles = [role.name for role in msg.author.roles]
                                for role in roles:
                                    if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower() or message.author == msg.author:
                                        return True
                    except:
                        return False
                elif msg.channel == message.channel and msg.author == message.author and ("thanks" in msg.content.lower() or "thnks" in msg.content.lower() or "thx" in msg.content.lower() or "thank you" in msg.content.lower() or "ty" in msg.content.lower().split() or "tysm" in msg.content.lower() or "thanku" in msg.content.lower() or "tanks" in msg.content.lower()):
                    return True
            try:
                helper_role = discord.utils.get(message.guild.roles, id=helper_roles[message.channel.id])
            except:
                await message.reply("There are no helper roles specified for this channel.")
                return
            m1 = await message.reply(f"The helper role for this channel, @{helper_role.name}, will automatically be pinged in 15 minutes. If your query has been resolved by then, please reply to this message with \"cancel\"")
            try:
                m3 = await client.wait_for("message", check=check, timeout=12*60)
                await message.reply(f"Ping cancelled by {m3.author.mention}")
                await m1.delete()
                await m3.delete()
            except:
                try:
                    m4 = await message.reply("The helper role will be pinged in 3 minutes. This is a reminder to cancel your ping if your question has been answered.")
                    m3 = await client.wait_for("message", check=check, timeout=3*60)
                    await message.reply(f"Ping cancelled by {m3.author.mention}")
                    await m1.delete()
                    await m4.delete()
                    await m3.delete()
                except:
                    await message.reply(f"{helper_role.mention}\n(Requested by {message.author.mention})")
                    await m1.delete()
                    await m4.delete()

        if message.content.lower() == "refresh keywords":
            await refreshKeywords()
            await message.reply("Keywords have been updated!")

        if message.channel.id == 929910420326727730:
            await refreshKeywords()

        try: # Old Keyword autoreply system
            if message.content.lower() in keywords.keys():
                await message.channel.send(keywords[message.content.lower()])
        except:
            pass

        if message.content.lower() == "refresh helpers": # Refresh number of helpers info in description of channel
            changed = []
            for chnl, role in helper_roles.items():
                try:
                    helper_role = discord.utils.get(message.guild.roles, id=role)
                    no_of_users = len(helper_role.members)
                    channel = client.get_channel(chnl)
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
                await message.reply("Done! Changed channels: " + ", ".join(changed))
            else:
                await message.reply("No changes were made.")

        if message.content.lower().startswith("remove all roles"): # For mods only
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles:
                roles_removed = []
                try:
                    user = message.mentions[0]
                except:
                    user = client.get_member(int(message.content.split()[3]))
                for role in user.roles:
                    if role.id != 578170681670369290: # Discord Mod role should not be removed
                        try:
                            await user.remove_roles(role)
                            roles_removed.append(role.name)
                        except:
                            pass
                await message.reply(f"Removed roles {roles_removed} from user {user.mention}")
        
        if message.content.lower().startswith("remove helper roles"): # For mods only
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                roles_removed = []
                try:
                    user = message.mentions[0]
                except:
                    user = client.get_member(int(message.content.split()[3]))
                for role in user.roles:
                    if "Helper" in role.name:
                        await user.remove_roles(role)
                        roles_removed.append(role.name)
                await message.reply(f"Removed helper roles {roles_removed} from user {user.mention}")

        if message.content.lower() == "reaction roles help": # How to use reaction roles autoreply
            await message.reply("""** GUIDE ON HOW TO USE REACTION ROLES WITH r/IGCSE BOT **

    First, make an embed using the command, changing the title and description(which will contain the emojis and their corresponding role name) as necessary
    ```
    embed
    title=Pick up your roles!
    description= **:safety_pin: — Pink**

    **:green_square:  — Verified**```

    Next, reply to the message saying `add rr` in the first line and  in the subsequent lines, `the emoji + space + the role id`. For example,
    ```
    add rr
    🧷 878507552143450142
    🟩  918711508110835732
    ```

    To save an embed's code, reply to the embed saying `to dict`.  Later, you can recreate the embed by saying `from dict` in the first line of a message and in the next line, paste the output of `to dict`. For example,  say:
    ```
    from dict
    {'color': 15844367, 'type': 'rich', 'description': '🧷 — Pink\n\n🟩  — Verified', 'title': 'Pick up your roles!'}
    ```
    Note: This does not save the reaction roles. Those are saved in #reaction-roles . Use that to add the reactions using `add rr` if you recreate the embed later.""")

        if message.content.lower() == "to dict": # Helper function to save an embed's code
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                msg = await message.channel.fetch_message(message.reference.message_id)
                await message.reply(msg.embeds[0].to_dict())
                await message.delete()

        if message.content.lower().startswith("from dict\n"): # Helper function to generate an embed from previously saved code
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                embed = discord.Embed.from_dict(eval("\n".join(message.content.split("\n")[1:])))
                await message.channel.send(embed=embed)
                await message.delete()

        if "get role ids" in message.content.lower(): # Get role ids of mentioned roles
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                await message.reply(str([role.id for role in message.role_mentions]))

        if message.content.lower() == "get all roles": # Get all role names and ids in server
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                content = ""
                for role in message.guild.roles:
                    if len(content) > 1900: await message.reply(content); content = ""
                    content += role.name + " " + str(role.id) + "\n"
                await message.reply(content)

        if message.content.lower().startswith("search roles by color "): # Get all roles of a specific color
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                content = ""
                for role in message.guild.roles:
                    if str(role.color) == message.content.split()[4]:
                        if len(content) > 1900: await message.reply(content); content = ""
                        content += role.name + " " + str(role.id) + "\n"
                await message.reply(content)

        if message.content.lower().startswith("add rr\n"): # Setup reaction roles for an embed
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                channel = client.get_channel(932454877915910144)
                reactionroles = await refreshReactionRoles()
                msg = await message.channel.fetch_message(message.reference.message_id)
                rroles = message.content.splitlines()[1:]
                changes = {}
                for rr in rroles:
                    emoji, roleid = rr.replace("  ", " ").split(" ")
                    roleid = int(roleid)
                    await msg.add_reaction(emoji)
                    changes[emoji] = roleid
                if message.reference.message_id in reactionroles.keys():
                    reactionroles[message.reference.message_id].update(changes)
                    update = True
                else:
                    update = False
                    reactionroles[message.reference.message_id] = changes
                content = f"{message.reference.message_id}\n"
                for emoji, roleid in reactionroles[message.reference.message_id].items():
                    content += f"{emoji} {roleid}\n"
                if update:
                    async for msg in channel.history(limit=500):
                        if str(message.reference.message_id) in msg.content:
                            await msg.edit(content=content)
                            break
                    else:
                        update = False
                if not update:
                    await channel.send(content)
                await message.reply("Done!", delete_after=3.0)
                await message.delete()

        if message.content.lower() == "refresh reaction roles":
            await refreshReactionRoles()

        if message.content.lower().startswith("caption\n") or message.content.lower().startswith("embed\n"): # Create an embed
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                title = message.content.split("title=")[1].split("description=")[0]
                desc = message.content.split("description=")[1]
                embedVar = discord.Embed(title=title, description=desc, colour = discord.Colour.green())
                await message.channel.send(embed=embedVar)
                await message.delete()

        if message.content.lower().startswith("edit title\n"): # Edit title of an embed
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                msg = await message.channel.fetch_message(message.reference.message_id)
                title = message.content.splitlines()[1]
                embedVar = discord.Embed(title=title, description=msg.embeds[0].description, colour = discord.Colour.green())
                await msg.edit(msg.content, embed=embedVar)
                await message.delete()

        if message.content.lower() == "restart bot": # Restart the bot
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                exit()

        # if message.content.lower() == "restore rep": # Was used to restore the rep from the backup when the rep system broke.
        #     if message.author.id == 604335693757677588:
                
        #         rep_dict = eval("""{721746952307605586: 570, 712945124283514890: 530, 783596915710754836: 298, 765580200465399808: 263, 203165702348210177: 235, 700877936223322234: 214, 341964434354470924: 207, 734367294221975612: 197, 686060470376857631: 167, 848569779761840148: 133, 751743710848483370: 116, 485761371397554227: 116, 570800412429385729: 100, 567638858783653899: 96, 589524545577156639: 92, 726310869444722708: 85, 708958254582988801: 84, 504939998358011915: 83, 321567907907764224: 75, 266571433663135744: 71, 695664505593528431: 69, 748345422262698115: 69, 632875536384917525: 67, 760137716452818945: 66, 793385686354755615: 60, 740555082805805076: 60, 441912103066927115: 53, 754390671930032129: 52, 553547912727101440: 47, 556994906271383574: 44, 841636317477470258: 43, 558620191638945803: 43, 516144105278013441: 42, 428179024842457099: 41, 576281953444167681: 41, 397895292357181442: 41, 325648951917281281: 39, 719450012186050621: 39, 444711163817754626: 38, 842244688077651999: 37, 337278055582007306: 37, 411115949287014401: 34, 433632183626891304: 32, 754589280873087058: 32, 937699482299142185: 31, 699687020695650466: 30, 722081906090573894: 30, 699715023584362576: 29, 757986094074691606: 29, 761611190026633220: 29, 436842758875906049: 28, 852612529489838101: 28, 651435756484558851: 27, 784356263710425110: 27, 737361121257980025: 26, 788756786856984586: 26, 287719770063765504: 24, 741665704838955020: 24, 732137176824938556: 24, 412794285898072077: 23, 605002928914432014: 22, 603955826398593047: 22, 569185887070453770: 20, 698958959242903572: 19, 797082160417734676: 19, 319910823348666370: 19, 405711525236441098: 19, 659748072968159239: 18, 698091985629741086: 17, 616602124817661962: 17, 788346294288252933: 17, 673628223539773441: 16, 740085206765010964: 15, 441580840863137820: 15, 277838115069231105: 14, 907314086600146974: 13, 553976768868909197: 13, 285248143753216001: 13, 261731498208657409: 13, 772111329494302731: 13, 762235836975546409: 13, 335758113758117888: 13, 733227768711479307: 13, 518739956743798797: 12, 622415725243400222: 12, 857240292922753035: 12, 713050616112480326: 12, 529861763865378838: 12, 532914066558156800: 11, 617989130898636849: 11, 575292604342861845: 11, 935158673335001129: 10, 728055551174508555: 10, 466221358876065813: 10, 683950471060520981: 10, 524220681018277888: 10, 781767282325323817: 10, 550665487319564295: 9, 894250226037194873: 9, 152239948056100864: 9, 648444619960483841: 9, 730476315572043821: 9, 782631800630411264: 9, 189309138185093120: 9, 625369819918630934: 9, 776150523346550814: 9, 260746839660167172: 8, 897707445156200478: 8, 710078982871056404: 8, 882594973340532776: 8, 339378365918347274: 8, 759790199117971527: 8, 859332308607565845: 8, 852638036864008202: 8, 864870046638800896: 8, 757676945294098453: 8, 339427888053092353: 8, 707527425378091020: 7, 752830793771909132: 7, 795223701502820371: 7, 458249047195516938: 7, 934774732514021396: 7, 423477192522072064: 7, 691176474157383681: 7, 373128356633247744: 7, 735068835299983380: 7, 490817900462997514: 7, 439957999855992833: 7, 828646828219564063: 7, 848993315382362142: 7, 737906247755366421: 6, 771025218302902302: 6, 746359729323900938: 6, 246712552879423488: 6, 918084463446073384: 6, 912292630036099092: 6, 486924472050384906: 6, 810618732351193229: 6, 767023532344868925: 6, 746192160625524766: 6, 562219930712277004: 6, 714218950895992842: 6, 838796212861272114: 6, 655787721935290378: 5, 757452739096871004: 5, 611358309626150923: 5, 649941648163471361: 5, 760174438577995788: 5, 693828224471269419: 5, 549634618635059201: 5, 674962758692765707: 5, 755373951479447553: 5, 800089678215774269: 5, 798751651191848961: 5, 771338328691572736: 5, 793516488446181417: 5, 734963396188831925: 5, 377796698929627150: 5, 841221442124120074: 5, 350437943376216074: 5, 810464864110641152: 5, 768602491041742898: 5, 269399173529337856: 5, 383512753240801280: 5, 832170514038128662: 5, 763296620094947328: 5, 332604133934759937: 5, 623172948315996222: 5, 829309410428977162: 5, 344707632499523585: 5, 758186338612150315: 4, 326288229961564170: 4, 719807591869317201: 4, 602882423738597404: 4, 601734647054991380: 4, 604335693757677588: 4, 535031091229229056: 4, 764704625919262741: 4, 934130765321617529: 4, 774128334971994142: 4, 827942869817753601: 4, 606089434471071763: 4, 683542733117587489: 4, 582563927976574976: 4, 492261500535308298: 4, 918122559168450581: 4, 873586884125786163: 4, 531382326261841933: 4, 203825587863683073: 4, 618600583288324106: 4, 750400693239545918: 4, 657238926716698634: 4, 755650551785717933: 4, 711609067256152075: 4, 139943504204791808: 4, 479607650078949416: 4, 487877577201942528: 4, 572346116792778753: 4, 412822613770108937: 3, 749916487887880232: 3, 541249717510602764: 3, 903295495273852999: 3, 671741451050418207: 3, 742627463196049502: 3, 568733062431506433: 3, 817136300867190796: 3, 563846479760850951: 3, 486901304988270594: 3, 740408620226969683: 3, 788737550721613824: 3, 799265009422565378: 3, 646769192812412947: 3, 763971240914190396: 3, 710130797943717971: 3, 647121313005174794: 3, 713428667728134154: 3, 774586423386963969: 3, 372457198560739328: 3, 622821975030628383: 3, 589446244254875661: 3, 754706533472010281: 3, 563304385489272843: 3, 757564602140721284: 3, 430736029281157123: 3, 267747981258653696: 3, 513012763811905536: 3, 243711114200875008: 3, 833207116138938418: 3, 602126447762735117: 3, 509709145222545429: 3, 411848651703582722: 3, 783049729701314561: 3, 762605399244275723: 3, 407081272293326858: 3, 746710411906252860: 3, 738594688696582215: 3, 238931083046027266: 3, 717978612778663977: 3, 694619655515668541: 3, 723978518744268912: 3, 831438907782332427: 3, 721974641622646854: 2, 581089090687205386: 2, 766470013544038440: 2, 539377743930982403: 2, 498123436003033088: 2, 718760756941815857: 2, 561599589455495178: 2, 837029195632082947: 2, 639735881334259732: 2, 721978425006620724: 2, 700261289410428938: 2, 296253335932239884: 2, 809850503093420032: 2, 531202495184240650: 2, 793854075611381842: 2, 909776886438199336: 2, 675428142466334752: 2, 739470336873070663: 2, 459589042325946369: 2, 842671592726200342: 2, 492732799137087488: 2, 932857022653796362: 2, 678912206015823881: 2, 625232733945331742: 2, 685858102645751854: 2, 923959729137520690: 2, 688690143145754631: 2, 764109699938910228: 2, 814477492999553074: 2, 629957313943568385: 2, 696928563148095520: 2, 827074264762810438: 2, 826142938203291658: 2, 758992728528257035: 2, 846606357788360714: 2, 697525483029397516: 2, 706247939953262623: 2, 883048632943771740: 2, 695216755848642560: 2, 606478568448458753: 2, 785034215786807317: 2, 529568754166661140: 2, 686933403559264447: 2, 692360840778875000: 2, 717970531781050398: 2, 855791196290023434: 2, 824250405155635251: 2, 832616735630688256: 2, 220118146185428992: 2, 763677226838523916: 2, 881714931311996930: 2, 722547459259105330: 2, 803925133957660683: 2, 826793821450272798: 2, 709655283953041408: 2, 753933776018604054: 2, 752730654923292733: 2, 798805427780321281: 2, 570721743682142248: 2, 330839929611354113: 2, 270904126974590976: 2, 401431577906642945: 2, 650011860535476264: 2, 506716228312891392: 2, 739182574173159505: 2, 875113991003861012: 2, 750632623017295914: 2, 405215696692314135: 2, 607215499314462722: 2, 528903306354098188: 2, 733625790431756288: 1, 562561501446012958: 1, 296551887929344000: 1, 861073699741368330: 1, 808451147269537832: 1, 618094668986581002: 1, 743485118273814590: 1, 824450258545278994: 1, 757452695496818708: 1, 808576827949842443: 1, 805366171758624788: 1, 588612543254233089: 1, 758182323249348608: 1, 739852763734867988: 1, 772020369845387276: 1, 778855097022808124: 1, 821808493773455390: 1, 703161494317039696: 1, 725267753770156094: 1, 768683737151569941: 1, 930369258251247656: 1, 458380775117815828: 1, 805818039500668968: 1, 836510220569542657: 1, 476641813327904770: 1, 646357832781791257: 1, 723933273046253620: 1, 773174949140627466: 1, 870206262476959754: 1, 629584261070061568: 1, 355374259171753984: 1, 554827199249907732: 1, 575791800757911555: 1, 907259508001218620: 1, 840905435371667456: 1, 395229460430848000: 1, 343361743998812172: 1, 739327677869195265: 1, 482462854205931521: 1, 817733757191716895: 1, 352533640519090187: 1, 789250205937696788: 1, 407086752860340224: 1, 784568157846503434: 1, 390915563607556097: 1, 931548300849577985: 1, 773114283764613132: 1, 766538430204346388: 1, 721429108982022274: 1, 874609661104500746: 1, 718477835303649331: 1, 662679912934670376: 1, 876373982268497920: 1, 916541990819205190: 1, 662907994161283072: 1, 692656712129183776: 1, 860848926247878657: 1, 518764437809790986: 1, 886626258098741329: 1, 858382949861687306: 1, 697298995336183848: 1, 823920114931597363: 1, 727185188110598235: 1, 428534641054449664: 1, 664160960449216523: 1, 534646200654364672: 1, 298359773823369236: 1, 620594731780669442: 1, 912282044875296828: 1, 762618940710191104: 1, 604258641222172672: 1, 779072381968842782: 1, 697258096489136272: 1, 491935072937705473: 1, 817083254195748924: 1, 796072809944055848: 1, 463996118414524427: 1, 756474839367286824: 1, 757933767238221834: 1, 753330670348271646: 1, 714426361279807531: 1, 723458061410369578: 1, 639830921767550986: 1, 648611819706908713: 1, 347999615783534592: 1, 781120603368980482: 1, 267375007938641922: 1, 689282670311637004: 1, 872031275798650961: 1, 763408883380912148: 1, 410010235768537089: 1, 225954278710312960: 1, 356818065696227331: 1, 510132057129877506: 1, 625750806276341782: 1, 775166505657958430: 1, 658520443308998706: 1, 595057166189199371: 1, 658741482370367488: 1, 350241575688732673: 1, 680017021479419907: 1, 686552137630744612: 1, 727358311439269918: 1, 494487241242968066: 1, 695591951738863616: 1, 594147411371491328: 1, 778230520709644309: 1, 692394802586845264: 1, 724038190406828132: 1, 756403371715592372: 1, 428789095808892929: 1, 900483813988237342: 1, 400630401116143616: 1, 330947004249145344: 1, 726900615413891133: 1, 821507473458331698: 1, 863147099993669707: 1, 789132769732984872: 1, 777608052806385695: 1, 844947134990385202: 1, 689844019026722910: 1, 456836070214991872: 1, 745039444888780812: 1, 830637270847324190: 1, 806075815300300842: 1, 406884337041014786: 1, 714922588882731089: 1, 881589862300516352: 1, 723408912463691777: 1, 811192076132941824: 1, 726013558566944769: 1, 702897112513249301: 1, 686508132645863506: 1, 782963136801013761: 1, 521419113218834435: 1, 418740356608425985: 1, 608113351863566337: 1, 349828961796358144: 1, 596349720180424726: 1, 483575972998807552: 1, 554640721970462732: 1, 531016012011929631: 1, 308050343441465344: 1, 689781349732843549: 1, 661164104593047552: 1, 773171429655052300: 1, 694498145165377536: 1, 690064921576472608: 1, 443032224917618689: 1, 647028795915894785: 1, 760887397872304208: 1, 611910835815579669: 1}""")
        #         for userid, rep in rep_dict.items():
        #             print(userid, rep)
        #             await changeRepNew(userid, rep)
        #     await message.reply("Done.")

        if message.content.lower().startswith("edit description\n"): # Edit the description of an embed
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                msg = await message.channel.fetch_message(message.reference.message_id)
                description = "\n".join(message.content.splitlines()[1:])
                for field in msg.embeds[0].fields:
                    try:
                        embed.add_field(name=field.name, value=field.value, inline=False)
                    except:
                        pass
                embedVar = discord.Embed(title=msg.embeds[0].title, description=description, colour = discord.Colour.green())
                await msg.edit(msg.content, embed=embedVar)
                await message.delete()

        if message.content.lower().startswith("addfield\n"): # Add a field to an embed
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles:
                msg = await message.channel.fetch_message(message.reference.message_id)
                name = message.content.splitlines()[1]
                value = "\n".join(message.content.splitlines()[2:])
                embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=msg.embeds[0].description)
                for field in msg.embeds[0].fields:
                    try:
                        embed.add_field(name=field.name, value=field.value, inline=False)
                    except:
                        pass
                embed.add_field(name=name, value=value, inline=False)
                await msg.edit(embed=embed)
                await message.delete()

        if message.content.lower().startswith(".clear") and len(message.content.split()) == 2: # Clear messages
                try:
                    num = int(message.content.split()[1])
                    roles = [role.name for role in message.author.roles]
                    if "Discord Mod" in roles or "Temp Mod" in roles:
                        if num <= 100:
                            try:
                                await message.channel.purge(limit=num+1)
                            except:
                                await message.reply("Oops! I can only delete messages sent in the last 14 days")
                        else:
                            await message.reply("Sorry, I can only delete up to 100 messages at a time.") # Safety feature
                except:
                    pass

        if message.content.lower() == 'joke': # A random joke
            req = requests.get("https://icanhazdadjoke.com/", headers={"Accept" : "application/json"})
            jsonobj = req.json()
            joke = jsonobj['joke']
            await message.channel.send(f"Here's your joke, {message.author.mention}.\n{joke}") 

        if message.channel.name == 'counting': # To facilitate #counting
            
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
                    await message.add_reaction("❌")
            except:
                await message.add_reaction("❌")

        if message.content.lower() == "ping": # A fun feature
            msg = await message.channel.send("Pong!")
            ping = msg.created_at.timestamp() - message.created_at.timestamp()
            await msg.edit(content=f"Ping: ``{round(ping*100)}``ms")

        if message.content.lower() == "pin": # Pin a message
            roles = [role.name for role in message.author.roles]
            for role in roles:
                if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower():
                    msg = await message.channel.fetch_message(message.reference.message_id)
                    await msg.pin()
                    await msg.reply(f"This message has been pinned by {message.author.mention}.")
                    await message.delete()
                    return

        if message.content.lower() == "unpin": # Unpin a message
            roles = [role.name for role in message.author.roles]
            for role in roles:
                if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower():
                    msg = await message.channel.fetch_message(message.reference.message_id)
                    await msg.unpin()
                    await msg.reply(f"This message has been unpinned by {message.author.mention}.")
                    await message.delete()
                    return

        if message.content.lower().startswith("~ "): # Message as the bot
            mod_roles = [role.name for role in message.author.roles]
            if "Discord Mod" in mod_roles or "Temp Mod" in mod_roles:
                try:
                    msg = await message.channel.fetch_message(message.reference.message_id)
                    await msg.reply(message.content[2:])
                except:
                    await message.channel.send(message.content[2:])
                await message.delete()
                
        if message.content.lower().startswith("? "): # Edit a message by the bot
            mod_roles = [role.name for role in message.author.roles]
            if "Discord Mod" in mod_roles or "Temp Mod" in mod_roles:
                try:
                    msg = await message.channel.fetch_message(message.reference.message_id)
                    if msg.author == client.user:
                        await msg.edit(content=message.content[2:])
                except:
                    pass
                await message.delete()

        if message.channel.id == 930274101321400361: # New emote suggestion
            msg = None
            if message.attachments:
                if "image" in message.attachments[0].content_type:
                    if message.content[0] == ":" and message.content[-1] == ":":
                        msg = await message.channel.send(f"New emote suggestion by {message.author.mention} `{message.clean_content}`", file=await message.attachments[0].to_file())
                    elif len(message.content) > 0:
                        msg = await message.channel.send(f"New emote suggestion by {message.author.mention} `:{message.clean_content}:`", file=await message.attachments[0].to_file())
                    else:
                        channel = await message.author.create_dm()
                        await channel.send("To submit an emote suggestion, please send an image, and a name for the emote in the form :name: , both in the same message in this channel. Please make sure they are sent in the same message or else it will not work.\n\nContact the mods by replying in this chat if you are facing any difficulties.")   
            await message.delete()
            if msg:
                await msg.add_reaction("👍")
                await msg.add_reaction("🔒")
                await msg.add_reaction("👎")
            else:
                channel = await message.author.create_dm()
                await channel.send("To submit an emote suggestion, please send an image, and a name for the emote in the form :name: , both in the same message in this channel. Please make sure they are sent in the same message or else it will not work.\n\nContact the mods by replying in this chat if you are facing any difficulties.")
        
        if ("nitro" in message.content.lower() and "http" in message.content.lower()) or ("http" in message.content.lower() and "@everyone" in message.clean_content.lower()) or ("http" in message.content.lower() and "gifts" in message.clean_content.lower()) or ("http" in message.content.lower() and "gift" in message.clean_content.lower()):
            user = message.author # Catch free nitro scams and mute the user
            role = discord.utils.get(message.guild.roles, id=787670627967959087)
            await user.add_roles(role)
            bot = message.guild.get_member(861445044790886467)
            mod_role = discord.utils.get(message.guild.roles, id=578170681670369290)
            await message.delete()
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [Mute]
    Username: {user.name}#{user.discriminator} ({user.id})
    Moderator: {bot.mention} 
    Reason: Sending a scam link for free nitro"""
            if ban_msg.splitlines()[1:] != last_ban_msg.content.splitlines()[1:]:
                await ban_msg_channel.send(ban_msg)
                log_channel = client.get_channel(792775200394575882)
                await log_channel.send(content=f"Transcript of message sent by {user.mention}:\n\n{message.content}")

        if message.channel.id == 893706892495425588: # #bot-talk - to talk as the bot
            try:
                channel = client.get_channel(int(message.content.splitlines()[0]))
                await channel.send("\n".join(message.content.splitlines()[1:]))
                await message.reply(f"Sent message to channel #{channel}")
            except:  
                try:
                    member = message.guild.get_member(int(message.content.splitlines()[0]))
                    channel = await member.create_dm()
                    await channel.send("\n".join(message.content.splitlines()[1:]))
                    await message.reply(f"Sent message to member {member}")
                except:
                    worked = False
                    for channel in client.get_all_channels():
                        try:
                            msg = await channel.fetch_message(int(message.content.splitlines()[0]))
                        except:
                            continue
                        await msg.reply("\n".join(message.content.splitlines()[1:]))
                        await message.reply(f"Sent message to channel #{channel} as a reply to message {msg.jump_url}")
                        worked = True
                    if not worked:
                        await message.reply("Error.")
                
        if "rep"==message.content.lower() or "leaderboard"==message.content.lower() or "rep leaderboard"==message.content.lower():
            leaderboard = await getLeaderboardNew() # Rep leaderboard
            chunks = [list(leaderboard.items())[x:x+9] for x in range(0, len(leaderboard), 9)] # Split into groups of 9
            
            pages = []
            for n,chunk in enumerate(chunks):
                embedVar = discord.Embed(title="Reputation Leaderboard", description=f"Page {n+1} of {len(chunks)}", colour = discord.Colour.green())
                for user, rep in chunk:
                    user_name = message.guild.get_member(user)
                    if rep == 0 or user_name == None:
                        channel = client.get_channel(692686505889628281)
                        await channel.send(f"User ID {user} having {rep} rep has been removed from the rep leaderboard")
                        await removeUser(user)
                    else:
                        embedVar.add_field(name=user_name, value=str(rep)+"\n", inline=True)
                        
                pages.append(embedVar)

            message = await message.reply(embed = pages[0])

            await message.add_reaction('⏮')
            await message.add_reaction('◀')
            await message.add_reaction('🔒')
            await message.add_reaction('▶')
            await message.add_reaction('⏭')

            i = 0
            reaction = None

            while True:
                if str(reaction) == '⏮':
                    i = 0
                    await message.edit(embed = pages[i])
                elif str(reaction) == '◀':
                    if i > 0:
                        i -= 1
                        await message.edit(embed = pages[i])
                elif str(reaction) == "🔒":
                    await message.clear_reactions()
                    return
                elif str(reaction) == '▶':
                    if i < len(pages) - 1:
                        i += 1
                        await message.edit(embed = pages[i])
                elif str(reaction) == '⏭':
                    i = len(pages) - 1
                    await message.edit(embed = pages[i])
                
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout = 30.0)
                    if user == client.user:
                        reaction, user = await client.wait_for('reaction_add', timeout = 30.0)
                    await message.remove_reaction(reaction, user)
                except:
                    break

            await message.clear_reactions()

        if "my rep"==message.content.lower():
            rep = await getRepNew(message.author.id)
            await message.reply(f"Hi {message.author.mention}, you have {rep} rep!")
        
        try:
            if message.content.lower().split()[0] == "rep":
                try:
                    for mention in message.mentions:
                        rep = await getRepNew(mention.id)
                        await message.reply(f"{mention} has {rep} rep!")
                except:
                    pass
        except:
            pass

        # if message.content.lower().startswith("i'm ") or message.content.lower().startswith("i am ") or message.content.lower().startswith("im "):
        #     await message.reply("Hi"+"m".join(message.clean_content.split("m")[1:])+", I'm r/IGCSE Bot!")

        if "discord.gg" in message.content.lower() and not ("discord.gg/igcse" in message.content.lower() or "discord.gg/yZAyR6x" in message.content.lower() or "discord.gg/6thform" in message.content.lower() or "discord.gg/ibo" in message.content.lower() or "discord.gg/homework" in message.content.lower() or "discord.gg/bXUAtcNUWc" in message.content.lower() or "discord.gg/memers" in message.content.lower() or "discord.gg/znotes" in message.content.lower() or "discord.gg/v5zzkHNZks" in message.content.lower()):
            roles = [role.name for role in message.author.roles] # Catch not allowed server invite links and mute
            for role in roles:
                if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower():
                    return
            user = message.author
            bot = message.guild.get_member(861445044790886467)
            mod_role = discord.utils.get(message.guild.roles, id=578170681670369290)
            await message.reply(f"{message.author.mention} has been muted for sending an invite link for another server.\nIf this action was done in error, {mod_role.mention} will review the mute and revoke it if necessary")
            await message.delete()
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            role = discord.utils.get(message.guild.roles, id=787670627967959087)
            await user.add_roles(role)
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [Mute]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {bot.mention} 
Reason: Sending invite link to another server"""
            await ban_msg_channel.send(ban_msg)
            log_channel = client.get_channel(792775200394575882)
            await log_channel.send(content=f"Transcript of message sent by {user.mention}:\n\n{message.content}")

        if ('hi' in message.content.lower().split() and client.user.mentioned_in(message)):
            await message.channel.send(f"Hi {message.author.mention}!")

        if ("you're welcome" in message.content.lower() or "youre welcome" in message.content.lower() or "ur welcome" in message.content.lower() or "u r welcome" in message.content.lower() or "your welcome" in message.content.lower() or "welcome" == message.content.lower() or 'no problem' in message.content.lower() or 'np' in message.content.lower().split() or 'np!' in message.content.lower().split() or 'yw' in message.content.lower().split()):
            try: # Add rep to message author
                msg = await message.channel.fetch_message(message.reference.message_id)
                if msg.author != message.author:
                    if not (message.author.mentioned_in(msg) and ('thanks' in msg.content.lower() or 'thank you' in msg.content.lower() or 'thx' in msg.content.lower() or 'tysm' in msg.content.lower() or 'thank u' in msg.content.lower() or 'thnks' in msg.content.lower() or 'tanks' in msg.content.lower() or "thanku" in msg.content.lower() or "ty" in msg.content.lower().split())):
                        rep = await addRepNew(message.author.id)
                        leaderboard = await getLeaderboardNew()
                        members = list(leaderboard.keys())[:3]
                        if leaderboard[members[-1]] == list(leaderboard.values())[len(members)]: # If 3rd and 4th position have same rep
                            members.append(list(leaderboard.keys())[len(members)]) # Add 4th position to list of reputed members
                        role = discord.utils.get(message.author.guild.roles, name="Reputed")
                        for m in role.members:
                            await m.remove_roles(role)
                        for member in members:
                            member = message.guild.get_member(member)
                            await member.add_roles(role)
                        await message.channel.send(f"Gave +1 Rep to {message.author.mention} ({rep})")
            except:
                pass

        if message.content.lower() == "scam" or message.content.lower() == "spam":
            try: # Scam/spam messages reported by the user
                msg = await message.channel.fetch_message(message.reference.message_id)

                roles = [role.name for role in msg.author.roles]
                for role in roles:
                    if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower():
                        await lowLikelihood(message)
                        return
                
                if "http" in msg.content.lower() or "www" in msg.content.lower() or ".com" in msg.content.lower():

                    roles = [role.name for role in message.author.roles]
                    for role in roles:
                        if "helper" in role.lower() or "discord mod" in role.lower() or "temp mod" in role.lower():
                            await spamMessage(msg, message.author)
                            return

                    fetchMessage = await message.channel.history(limit=5).flatten()
                    for m in fetchMessage:
                        if m.content == msg.content and m.id != msg.id:
                            await spamMessage(msg, message.author)
                            return

                    channels = message.guild.text_channels
                    channels.remove(msg.channel)

                    for channel in channels:
                        fetchMessage = await channel.history(limit=5).find(lambda m: m.content == msg.content) 
                        if fetchMessage:
                            await spamMessage(msg, message.author)
                            return
                    await lowLikelihood(message)
                else:
                    await lowLikelihood(message)
            except:
                await message.reply("Hi there! If you have encountered a spam/scam message, kindly **reply** to the scam message saying 'scam'.\n\nThe bot will evaluate the message and potentially mute the sender.")

        if message.content.lower() in text_prompts.keys():
            await message.channel.send(text_prompts[message.content.lower()])

        if 'thanks' in message.content.lower() or 'thank you' in message.content.lower() or 'thx' in message.content.lower() or 'tysm' in message.content.lower() or 'thank u' in message.content.lower() or 'thnks' in message.content.lower() or 'tanks' in message.content.lower() or "thanku" in message.content.lower() or "ty" == message.content.lower() or "ty" in message.content.lower().split():
            mentions = message.mentions # Give rep
            for mention in mentions:
                if mention == message.author:
                    await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep yourself!")
                    return
                if mention.bot:
                    await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep a bot!")
                    return
                rep = await addRepNew(mention.id)
                leaderboard = await getLeaderboardNew()
                members = list(leaderboard.keys())[:3]
                if leaderboard[members[-1]] == list(leaderboard.values())[len(members)]: # If 3rd and 4th position have same rep
                    members.append(list(leaderboard.keys())[len(members)]) # Add 4th position to list of reputed members
                role = discord.utils.get(message.author.guild.roles, name="Reputed")
                for m in role.members:
                    await m.remove_roles(role)
                for member in members:
                    member = message.guild.get_member(member)
                    await member.add_roles(role)
                await message.channel.send(f"Gave +1 Rep to {mention.mention} ({rep})")
            try:
                backup_channel = client.get_channel(869753809428160602)
                line = str(leaderboard)
                msgs = [line[i:i+2000] for i in range(0, len(line), 2000)]
                for msg in msgs:
                    await backup_channel.send(msg)
            except:
                pass
        
        # Reminding users to get session roles: (not in use anymore)
        # if not message.author.bot:
        #     try:
        #         user_roles = set([role.name for role in message.author.roles])
        #         session_roles = set(["M/J 2020", "O/N 2021", "F/M 2022", "M/J 2022", "O/N 2022",
        # "IGCSE Alumni", "NOT IGCSE", "F/M 2023", "M/J 2023", "O/N 2023", "CAIE", "Edexcel"])

        #         if not (user_roles & session_roles):
        #             channel = await message.author.create_dm()
        #             messages = await channel.history(limit=1).flatten()
        #             if not messages:
        #                 await channel.send(f"""Hey {message.author.mention}! Welcome to r/IGCSE :)\nWe noticed you haven't picked your session roles.\nGo to {client.get_channel(669287399041269791).mention} to pick when you are taking the exams.\nThank you and have a great time at r/IGCSE!\n\n> If you believe this message was sent in error, please contact {message.guild.get_member(604335693757677588).mention} (Flynn#5627)""")
        #     except:
        #         pass

        if message.content.lower().startswith('change rep'): # Change someone's rep
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[2]))
                except:
                    user = message.guild.get_member_named(message.content.split()[2])
            new_rep = int(message.content.split()[3])
            await changeRepNew(user.id,new_rep)
            leaderboard = await getLeaderboardNew()
            members = list(leaderboard.keys())[:3]
            if leaderboard[members[-1]] == list(leaderboard.values())[len(members)]: # If 3rd and 4th position have same rep
                members.append(list(leaderboard.keys())[len(members)]) # Add 4th position to list of reputed members
            role = discord.utils.get(message.author.guild.roles, name="Reputed")
            for m in role.members:
                await m.remove_roles(role)
            for member in members:
                member = message.guild.get_member(member)
                await member.add_roles(role)
            await message.channel.send("Done!")

        if message.channel.id == 758562162616303658: # New suggestion
            try:
                msg = await message.channel.fetch_message(message.reference.message_id)
                embed = discord.Embed(title=msg.embeds[0].title, colour=msg.embeds[0].colour, description=msg.embeds[0].description)
                for field in msg.embeds[0].fields:
                    try:
                        embed.add_field(name=field.name, value=field.value, inline=False)
                    except:
                        pass
                embed.add_field(name=message.author, value=message.clean_content, inline=False)
                await msg.edit(embed=embed)
                await message.delete()
            except: # If they don't reply to a specific suggestion
                if not ("Discord Mod" in [role.name for role in message.author.roles]):
                    channel = await message.author.create_dm()
                    await channel.send(f"Hi there! You sent a message on the #suggestions channel. If you would like to comment on a suggestion, reply to the suggestion message directly in #suggestions with your comment. If you would like to create a new suggestion with the text, click on the ✅ reaction in the below message. Thank you!")
                    m = await channel.send(message.content)
                    await m.add_reaction("✅")
                    await message.delete()

        if message.content.lower() == "suggest" or message.content.lower() == "suggestion" or message.content.lower() == "vote":
            try: # Create new suggestion
                msg = await message.channel.fetch_message(message.reference.message_id)
                channel = client.get_channel(758562162616303658)
                embedVar = discord.Embed(title=f"Suggestion by {msg.author}", description=f"Total Votes: 0\n\n{'🟩'*10}\n\nSuggestion: {msg.clean_content}\n(via: {message.author})", colour = discord.Colour.green())
                if message.attachments:
                    if "image" in message.attachments[0].content_type:
                        embedVar.set_image(url=message.attachments[0].url)
                msg1 = await channel.send(embed=embedVar)
                await msg.reply("This suggestion has been noted! Thank you!")
                await msg1.add_reaction('✅')
                await msg1.add_reaction("🟢")
                await msg1.add_reaction("🔴")
                await msg1.add_reaction('❌')
                await message.delete()
            except:
                pass

        if message.content.lower() == "poll": # Create an in-channel poll
            try:
                msg = await message.channel.fetch_message(message.reference.message_id)
                embedVar = discord.Embed(title=f"Poll by {msg.author}", description=f"Total Votes: 0\n\n{'🟩'*10}\n\nVote: {msg.clean_content}\n(via: {message.author})", colour = discord.Colour.green())
                msg1 = await message.channel.send(embed=embedVar)
                await msg1.add_reaction('✅')
                await msg1.add_reaction('❌')
                await message.delete()
            except:
                pass

        if len(message.content.split()) > 0 and message.content.lower().split()[0] == '.ban': # Ban a user
            action_type = "Ban"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or message.author.id == 604335693757677588):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            reason = " ".join(message.content.split()[2:])
            try:
                await user.send(f"Hi there from r/IGCSE. You have been banned from the server due to {reason}. If you feel this ban was done in error, to appeal your ban, please fill the form below.\nhttps://forms.gle/Df5JKRKjcBo8o8s99")
            except:
                pass
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
            await message.guild.ban(user, delete_message_days=1)
            await message.channel.send(f"{user.name}#{user.discriminator} has been banned.")
            await ban_msg_channel.send(ban_msg)
        
        if len(message.content.split()) > 0 and message.content.lower().split()[0] == '.kick': # Kick a user
            action_type = "Kick"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or message.author.id == 604335693757677588):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            reason = " ".join(message.content.split()[2:])
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
            await message.guild.kick(user)
            await message.channel.send(f"{user.name}#{user.discriminator} has been kicked.")
            await ban_msg_channel.send(ban_msg)

        if len(message.content.split()) > 0 and message.content.lower().split()[0] == '.unban':  # Unban a user
            action_type = "Unban"
            user = int(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or message.author.id == 604335693757677588):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            reason = " ".join(message.content.split()[2:])
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            
            bans = await message.guild.bans()
            for ban in bans:
                if ban.user.id == user:
                    await message.guild.unban(ban.user)
                    await message.channel.send(f"{ban.user.name}#{ban.user.discriminator} has been unbanned.")
                    ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {ban.user.name}#{ban.user.discriminator} ({ban.user.id})
Moderator: {mod} 
Reason: {reason}"""
                    await ban_msg_channel.send(ban_msg)
                    return

        if len(message.content.split()) > 0 and message.content.lower().split()[0] == '.warn':  # Warn a user
            action_type = "Warn"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                return
            reason = " ".join(message.content.split()[2:])
            ban_msg_channel = client.get_channel(896386473572569098)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
            await message.channel.send(f"{user.name}#{user.discriminator} has been warned.")
            await ban_msg_channel.send(ban_msg)
            channel = await user.create_dm()
            await channel.send(f"You have been warned in r/IGCSE by moderator {message.author} for \"{reason}\".\n\nPlease be mindful in your further interaction in the server to avoid further action being taken against you, such as a ban or a mute.")

        if message.content.startswith('.mute'):  # Mute a user
            action_type = "Mute"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            reason = " ".join(message.content.split()[2:])
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
            role = discord.utils.get(user.guild.roles, name="Muted")
            await user.add_roles(role)
            await ban_msg_channel.send(ban_msg)
            await message.channel.send(f"{user.name}#{user.discriminator} has been muted.")

        if message.content.startswith('.unmute'):  # Unmute a user
            action_type = "Unmute"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod}"""
            role = discord.utils.get(user.guild.roles, name="Muted")
            await user.remove_roles(role)
            await ban_msg_channel.send(ban_msg)
            await message.channel.send(f"{user.name}#{user.discriminator} has been unmuted.")

        if message.content.startswith('.untimeout'):  # Untimeout a user
            action_type = "Remove Timeout"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            await user.edit(timeout=None)
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod}"""
            await ban_msg_channel.send(ban_msg)
            await message.channel.send(f"Timeout has been removed from {user.name}#{user.discriminator}.")

        if message.content.startswith('.timeout'): # Timeout a user
            action_type = "Timeout"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles or "VC Admin" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                return
            time_ = message.content.split()[2]
            reason = " ".join(message.content.split()[3:])
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
            await user.edit(timeout=discord.utils.utcnow() + datetime.timedelta(seconds=seconds))
            human_readable_time = f"{seconds // 86400}d {(seconds % 86400) // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s"
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)"""
            await ban_msg_channel.send(ban_msg)
            await message.channel.send(f"{user.name}#{user.discriminator} has been put on time out until <t:{int(time.time()) + seconds}>, which is <t:{int(time.time()) + seconds}:R>.")
        
        if message.content.startswith('!tempmute'):  # Not in use anymore
            action_type = "Temp Mute"
            try:
                user = message.mentions[0]
            except:
                try:
                    user = message.guild.get_member(int(message.content.split()[1]))
                except:
                    user = message.guild.get_member_named(message.content.split()[1])
            mod = message.author.mention
            mod_roles = [role.name for role in message.author.roles]
            if not ("Discord Mod" in mod_roles or "Temp Mod" in mod_roles):
                await message.channel.send(f"Sorry {mod}, you don't have the permission to perform this action.")
                return
            user_roles = [role.name for role in user.roles]
            if "Discord Mod" in user_roles:
                        await message.channel.send(f"Sorry {mod}, you can't {action_type.lower()} a Moderator!")
                        return
            time_ = message.content.split()[2]
            reason = " ".join(message.content.split()[3:])
            ban_msg_channel = client.get_channel(690267603570393219)
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
            ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {user.name}#{user.discriminator} ({user.id})
Moderator: {mod} 
Reason: {reason}
Duration: {time_}"""
            await ban_msg_channel.send(ban_msg)
        
        if message.content.lower() == "study ping": # Conduct a study session ping
            roles = [role.name for role in message.author.roles]
            if "Discord Mod" in roles or "Temp Mod" in roles or "IGCSE Helper" in roles or "Study Session Host" in roles:
                role = message.guild.get_role(study_roles[message.channel.id])
                study_sesh_channel = client.get_channel(941276796937179157)
                msg_history = await study_sesh_channel.history(limit=3).flatten()
                for msg in msg_history:
                    if str(message.author.mention) in msg.content and (msg.created_at.replace(tzinfo=None) + datetime.timedelta(minutes=60) > datetime.datetime.utcnow()):
                        await message.reply("Please wait until one hour after your previous ping to start a new study session.")
                        return
                voice_channel = message.author.voice
                if voice_channel == None:
                    await message.reply("You must be in a voice channel to use this command.")
                else:
                    await study_sesh_channel.send(f"{role.mention} - Requested by {message.author.mention} - Please join {voice_channel.channel.mention}")
                    await message.reply(f"Started a {role.name.lower().replace(' study ping', '').title()} study session at {voice_channel.channel.mention}.")
                    await voice_channel.channel.edit(name=f"{role.name.lower().replace(' study ping', '').title()} Study Session")
    
    except:
        content = f"""Message Content - {message.content}
Message Author - {message.author}
Message ID - {message.id}
Message Channel - {message.channel}
Message Link - {message.jump_url}
Traceback - {traceback.format_exc()}"""
        await client.get_channel(936179101130190919).send(content) # Send bug report to bot error log channel
        

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel: # When user leaves a voice channel
        if "study session" in before.channel.name.lower() and before.channel.members == []: # If the study session is over
            await before.channel.edit(name="General") # Reset channel name

client.run(TOKEN)
