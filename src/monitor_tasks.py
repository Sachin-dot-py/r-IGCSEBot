from bot import bot, discord, tasks, pymongo, bot, guild
from constants import LINK, GUILD_ID, FORCED_MUTE_ROLE, MODLOG_CHANNEL_ID
import time, traceback
from data import AUTO_SLOWMODE_CHANNELS
import datetime

async def togglechannellock(channel_id, unlock, *, unlocktime=0):
    everyone = bot.get_guild(GUILD_ID).default_role
    channel = bot.get_channel(channel_id)
    overwrite = channel.overwrites_for(everyone)
    overwrite.send_messages_in_threads = unlock
    overwrite.send_messages = unlock
    try:
        await channel.set_permissions(everyone, overwrite=overwrite)
        await channel.send(f"Channel has been {'unl' if unlock else 'l'}ocked.")
        if not unlock:
            await channel.send(f"Unlocking channel <t:{unlocktime}:R>.")

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("failed to set permissions")

async def toggleforumlock(thread_id, unlock, unlocktime):
    thread = bot.get_channel(thread_id)
    try:
        thread = await thread.edit(locked= not unlock)
        await thread.send(f"Thread has been {'unl' if unlock else 'l'}ocked.")
        if not unlock:
            await thread.send(f"Unlocking thread <t:{unlocktime}:R>.")
    except Exception as e:
        print(traceback.format_exc())
        print(e)

@tasks.loop(seconds=20)
async def checklock():
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    clocks = db["channellock"]
    flocks = db["forumlock"]
    try:
        results = clocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                ult = clocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                print(result["channel_id"])
                await togglechannellock(result["channel_id"], result["unlock"], unlocktime=ult)

                clocks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

        results = flocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                ult = flocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                print(result["thread_id"])
                await toggleforumlock(result["thread_id"], result["unlock"], unlocktime=ult)
                flocks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

    except Exception:
        print(traceback.format_exc())

@tasks.loop(seconds=20)
async def checkmute():
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    mute = db["mute"]
    Logging = bot.get_channel(MODLOG_CHANNEL_ID)
    timern = int(time.time()) + 1
    try:
        results = mute.find({"muted": True})
        for result in results:
            if result["unmute_time"] <= str(timern):
                user_id = int(result["user_id"])
                guild = bot.get_guild(GUILD_ID)
                # The user ID may not be present in cache.
                user = guild.get_member(user_id) or await guild.fetch_member(user_id)
                if user == None:
                    mute.delete_many({"user_id": user_id})
                    return
                forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
                await user.remove_roles(forced_mute_role)
                #mute.update_one({"_id": result["_id"]}, {"$set": {"muted": False}})
                embed = discord.Embed(description="Go Study Mode Deactivated", colour=discord.Colour.green())                
                embed.set_author(name="MongoDB#0082", icon_url="https://cdn.discordapp.com/attachments/947859228649992213/1196753678342819933/mongodb.png?ex=65b8c6b7&is=65a651b7&hm=db7fdb12435ba54299497dfb26f65dac5993caa8b48b976cf01238233c54a508&")
                embed.add_field(name="User", value=f"{user.mention}", inline=False)
                embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
                embed.add_field(name="ID", value= f"```py\nUser = {bot.user.id}\nRole = {FORCED_MUTE_ROLE}```", inline=False)
                embed.set_footer(text=f"r/IGCSE Bot#2063")
                await Logging.send(embed=embed)
                mute.delete_one({"_id": result["_id"]})
    except Exception:
        print(traceback.format_exc())

@tasks.loop(seconds=30)
async def handle_slowmode():
    for channel_id in AUTO_SLOWMODE_CHANNELS:
        slowmode = 3
        current_time = datetime.datetime.now()
        time_15s_ago = current_time - datetime.timedelta(seconds=15)
        channel = bot.get_channel(channel_id)
        if not channel: continue
        messages_in15s = await channel.history(after=time_15s_ago, limit=300).flatten()
        number_of_messages = len(messages_in15s)
        if number_of_messages <= 10:
            slowmode = 0
            if channel.slowmode_delay != 0:
                await channel.edit(slowmode_delay=slowmode)
            continue

        user_messages = {}

        for message in messages_in15s:
            if message.author.bot: continue
            if message.author.id not in user_messages:
                user_messages[message.author.id] = 1
            else:
                user_messages[message.author.id] += 1
        
        sorted_user_messages = dict(sorted(user_messages.items(), key=lambda x: x[1], reverse=True))
        for user_id, message_count in sorted_user_messages.items():
            if message_count >= 12:
                message = await channel.send(f"<@{user_id}> You are sending too many messages. Please slow down.")
                await message.delete(delay=10)
            
        if number_of_messages > 60:
            # 4 messages per second, will likely never happen
            slowmode = 120
        elif number_of_messages > 45:
            # chat is absolute chaos
            slowmode = 60
        elif number_of_messages > 30:
            slowmode = 45
        elif number_of_messages > 20:
            slowmode = 15
        elif number_of_messages > 15:
            slowmode = 7
            
        if channel.slowmode_delay != slowmode:
            await channel.edit(slowmode_delay=slowmode)

handle_slowmode.start()