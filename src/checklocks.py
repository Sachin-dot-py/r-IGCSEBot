from constants import LINK
from bot import tasks, pymongo

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

    except Exception as e:
        print(e)