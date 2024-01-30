from bot import bot, discord, pymongo, time
from constants import LINK, GUILD_ID, MODLOG_CHANNEL_ID
from roles import is_bot_developer, is_moderator

@bot.slash_command(name="channellock", description="Locks a channel at a specified time")
async def Channellockcommand(interaction: discord.Interaction,
                        channelinput: discord.TextChannel =  discord.SlashOption(name="channel_name", description="Which channel do you want to lock?", required=True),
                        locktime: str = discord.SlashOption(name="lock_time", description="At what time do you want the channel to be locked?", required=True),
                        unlocktime: str = discord.SlashOption(name="unlock_time", description="At what time do you want the channel to be unlocked?", required=True)):
        timenow = int(time.time()) + 1
        await interaction.response.defer(ephemeral=True)
        if not await is_moderator(interaction.user) and not await is_bot_developer(interaction.user):
                await interaction.send(f"Sorry {interaction.user.mention}," " you don't have the permission to perform this action.", ephemeral=True)
                return
        
        if locktime == "resolveall" and unlocktime == "!@#$%^&*()":
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            locks = db["channellock"]
            results = locks.find({"resolved": False})
            for result in results:
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})
            await interaction.send(f"Resolve Successful!", ephemeral=True)
                
        overwrite = channelinput.overwrites_for(interaction.guild.default_role)                
        if overwrite.send_messages == False and overwrite.send_messages_in_threads == False:
            await interaction.send(f"Sorry {interaction.user.mention}," " this channel has already been locked. please unlock and try again.", ephemeral=True)
            return
        
        if unlocktime == 'now':
            locktime = 0
            unlocktime = time.time() + 5

        try:
                locktime = int(locktime)
                unlocktime = int(unlocktime)
        except ValueError:
                await interaction.send(f"Sorry {interaction.user.mention}," " values of the time should be positive integers only. please try again.", ephemeral=True)
                return
        
        if locktime < 0 or unlocktime < 0:
                await interaction.send(F"{'L' if locktime < 0 else 'Unl'}ocktime is invalid. please try with values greater than 0.", ephemeral=True)
                return
        
        elif locktime >= unlocktime :
                await interaction.send("the unlock time has to be after lock time. please try again.", ephemeral=True)
                return

        elif locktime < timenow or unlocktime < timenow:
            await interaction.send(F"{'L' if locktime < timenow else 'Unl'}ocktime has already passed. the current time is {round(time.time())}. please try again.", ephemeral=True)
            return

        unixlocktime = f"<t:{locktime}:F>"
        unixunlocktime = f"<t:{unlocktime}:F>"
        channel_id = f"<#{channelinput.id}>"

        await interaction.send(f"{channel_id} is scheduled to lock on {unixlocktime} and unlock on {unixunlocktime}", ephemeral=True)

        user_id = f"<@{interaction.user.id}>"
        channel_id = f"<#{channelinput.id}>"
        Logging = bot.get_channel(MODLOG_CHANNEL_ID)
        embed = discord.Embed(description="Scheduled Channel Lockdown", colour=discord.Colour.red())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Locked Channel", value=f"{channel_id}", inline=False)
        embed.add_field(name="Lock time", value=f"<t:{locktime}:R>", inline=False)
        embed.add_field(name="Unlock time", value=f"<t:{unlocktime}:R>", inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nChannel = {channelinput.id}```", inline=False)
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        await Logging.send(embed=embed)  
        
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        locks = db["channellock"]

        locks.insert_one({"_id": "l" + str(timenow), "channel_id": channelinput.id,
                        "unlock": False, "time": locktime,
                        "resolved": False})

        locks.insert_one({"_id": "u" + str(timenow), "channel_id": channelinput.id,
                        "unlock": True, "time": unlocktime,
                        "resolved": False})
        
        await channelinput.send(f"This channel has been scheduled to lock <t:{max(locktime, timenow)}:R>.")
        
@bot.slash_command(name="forumlock", description="Locks a forum thread at a specified time (for mods)")
async def Forumlockcommand(interaction: discord.Interaction, threadinput: discord.Thread = discord.SlashOption(name="thread_name", description="Which thread do you want to lock?", required=True), locktime: str = discord.SlashOption(name="lock_time", description="At what time do you want the thread to be locked?", required=True), unlocktime: str = discord.SlashOption(name="unlock_time", description="At what time do you want the thread to be unlocked?", required=True)):
        timenow = int(time.time()) + 1
        await interaction.response.defer(ephemeral=True)
        if not await is_moderator(interaction.user) and not await is_bot_developer(interaction.user):
                await interaction.send(f"Sorry {interaction.user.mention}," " you don't have the permission to perform this action.", ephemeral=True)
                return

        if unlocktime == 'now':
            locktime = 0
            unlocktime = time.time() + 5

        if locktime == "resolveall" and unlocktime == "!@#$%^&*()":
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            locks = db["forumlock"]
            results = locks.find({"resolved": False})
            for result in results:
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})
            await interaction.send(f"Resolve Successful!", ephemeral=True)                

        if threadinput.locked == True:
            await interaction.send(f"Sorry {interaction.user.mention}," " the thread has already been locked. please unlock and try again.", ephemeral=True)
            return


        try:
                locktime = int(locktime)
                unlocktime = int(unlocktime)
        except ValueError:
                await interaction.send(f"Sorry {interaction.user.mention}," " values of the time should be positive integers only. please try again.", ephemeral=True)
                return
        
        if locktime < 0 or unlocktime < 0:
                await interaction.send(F"{'L' if locktime < 0 else 'Unl'}ocktime is invalid. please try with values greater than 0.", ephemeral=True)
                return
        
        elif locktime >= unlocktime :
                await interaction.send("the unlock time has to be after lock time. please try again.", ephemeral=True)
                return
        
        elif locktime < timenow or unlocktime < timenow:
            await interaction.send(F"{'L' if locktime < timenow else 'Unl'}ocktime has already passed. the current time is {round(time.time())}. please try again.", ephemeral=True)
            return

        unixlocktime = f"<t:{locktime}:F>"
        unixunlocktime = f"<t:{unlocktime}:F>"
        thread_id = f"<#{threadinput.id}>"
        
        await interaction.send(f"{thread_id} is been scheduled to lock on {unixlocktime} and unlock on {unixunlocktime}", ephemeral=True)

        user_id = f"<@{interaction.user.id}>"
        thread_id = f"<#{threadinput.id}>"
        Logging = bot.get_channel(MODLOG_CHANNEL_ID)
        embed = discord.Embed(description="Scheduled Forum Lockdown", colour=discord.Colour.red())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Locked Thread", value=f"{thread_id}", inline=False)
        embed.add_field(name="Lock time", value=f"<t:{locktime}:R>", inline=False)
        embed.add_field(name="Unlock time", value=f"<t:{unlocktime}:R>", inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nThread = {threadinput.id}```", inline=False)
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        await Logging.send(embed=embed)        
        
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        lock = db["forumlock"]

        lock.insert_many([
                {"_id": "l" + str(timenow), "thread_id": threadinput.id,
                        "unlock": False, "time": locktime,
                        "resolved": False},
                {"_id": "u" + str(timenow), "thread_id": threadinput.id,
                        "unlock": True, "time": unlocktime,
                        "resolved": False}     
                ])

        await threadinput.send(f"this thread has been scheduled to lock <t:{max(locktime, timenow)}:R> successfully.")
