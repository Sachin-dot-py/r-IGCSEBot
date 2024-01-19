from bot import pymongo
from constants import LINK
from datetime import datetime


class ReactionRolesDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.reaction_roles = self.db.reaction_roles
    
    def new_rr(self, data):
        self.reaction_roles.insert_one({"reaction": data[0], "role": data[1], "message": data[2]})

    def get_rr(self, reaction, msg_id):
        result = self.reaction_roles.find_one({"reaction": reaction, "message": msg_id})
        if result is None:
            return None
        else:
            return result

rrdb = ReactionRolesDB(LINK)

class GuildPreferencesDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.pref = self.db.guild_preferences

    def set_pref(self, pref: str, pref_value, guild_id: int):
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

    def change_rep(self, user_id, new_rep, guild_id):
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


repdb = ReputationDB(LINK)

class StickyMessageDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi("1"))
        self.db = self.client.IGCSEBot
        self.stickies = self.db.stickies

    def get_length_stickies(self, criteria={}):
        return len(list(self.stickies.find(criteria)))

    async def check_stick_msg(self, reference_msg):
        message_channel = reference_msg.channel
        if self.get_length_stickies() > 0:
            for stick_entry in self.stickies.find({"channel_id": message_channel.id}):
                if not stick_entry["sticking"]:
                    prev_stick = {"message_id": stick_entry["message_id"]}

                    self.stickies.update_one(prev_stick, {"$set": {"sticking": True}})
                    stick_message = await message_channel.fetch_message(stick_entry["message_id"])
                    is_present_history = False

                    async for message in message_channel.history(limit=3):
                        if message.id == stick_entry["message_id"]:
                            is_present_history = True
                            self.stickies.update_one(prev_stick, {"$set": {"sticking": False}})

                    if not is_present_history:
                        stick_embed = stick_message.embeds

                        self.stickies.delete_one(prev_stick)
                        await stick_message.delete()

                        new_embed = await message_channel.send(embeds=stick_embed)
                        self.stickies.insert_one({"channel_id": message_channel.id, "message_id": new_embed.id, "sticking": True})

                        self.stickies.update_one({"message_id": new_embed.id}, {"$set": {"sticking": False}})

    async def stick(self, reference_msg):
        embeds = reference_msg.embeds
        if embeds == [] or self.get_length_stickies({"message_id": reference_msg.id}) > 0:
            return
        await reference_msg.edit(embed=embeds[0].set_footer(text="Stuck"))

        self.stickies.insert_one({"channel_id": reference_msg.channel.id, "message_id": reference_msg.id, "sticking": False})
        await self.check_stick_msg(reference_msg)

        return True

    async def unstick(self, reference_msg):
        embeds = reference_msg.embeds
        if embeds == []:
            return
        await reference_msg.edit(embed=embeds[0].remove_footer())
        for stick_entry in self.stickies.find({"channel_id": reference_msg.channel.id}):
            if stick_entry["message_id"] == reference_msg.id:
                self.stickies.delete_one({"message_id": reference_msg.id})

        return True

smdb = StickyMessageDB(LINK)

class KeywordsDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.keywords = self.db.keywords

    def get_keywords(self, guild_id: int):
        result = self.keywords.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0})
        return {i['keyword'].lower(): i['autoreply'] for i in result}
    
    def keyword_list(self, guild_id: int):
        return self.keywords.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0})

    def add_keyword(self, keyword: str, autoreply: str, guild_id: int):
        result = self.keywords.insert_one({"keyword": keyword.lower(), "autoreply": autoreply, "guild_id": guild_id})
        return result

    def remove_keyword(self, keyword: str, guild_id: int):
        result = self.keywords.delete_one({"keyword": keyword.lower(), "guild_id": guild_id})
        return result

kwdb = KeywordsDB(LINK)

class PunishmentsDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.punishment_history = self.db.punishment_history
    
    def add_punishment(self, case_id: int, action_against: int, action_by: int, reason: str, action: str, when: datetime = datetime.utcnow(), duration: str = None):
        self.punishment_history.insert_one({
            "case_id": case_id,
            "action_against": str(action_against),
            "action_by": str(action_by),
            "reason": reason,
            "action": action,
            "duration": duration,
            "when": when
        })
    
    def get_punishments_by_user(self, user_id: int):
        return self.punishment_history.find({"action_against": str(user_id)})

punishdb = PunishmentsDB(LINK)