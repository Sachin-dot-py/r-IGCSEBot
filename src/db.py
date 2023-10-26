from constants import LINK
from bot import pymongo

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