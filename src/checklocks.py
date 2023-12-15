from constants import LINK, GUILD_ID
from bot import bot, tasks, pymongo, discord
import time
import traceback
from roles import get_role

async def togglechannellock(channelid, unlock, *, unlocktime=0):
    """Function for locking/unlocking a discord channel"""

    everyonerole = bot.get_guild(GUILD_ID).default_role

    channel = bot.get_channel(channelid)
    overwrite = channel.overwrites_for(everyonerole)
    overwrite.send_messages = unlock

    try:
        await channel.set_permissions(everyonerole, overwrite=overwrite)
        await channel.send(f"{'Unl' if unlock else 'L'}ocked channel.")

        if not unlock:
            # If the channel was locked, send another embed with unlock time
            embed = discord.Embed(description=f"Unlocking channel <t:{unlocktime}:R>.")
            await channel.send(embed=embed)

    except:
        print("failed to set permissions")

@tasks.loop(seconds=60)
async def checklocks():
    """Checks the database every 60 seconds to see if anything needs to be locked or unlocked """
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    locks = db["channellock"]
    try:
        results = locks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                # finds the unlock time
                ult = locks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await togglechannellock(result["channelid"], result["unlock"], unlocktime=ult)

                # Resolves the database entry (to avoid repeated locking/unlocking)
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

    except Exception:
        print(traceback.format_exc())
