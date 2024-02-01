from bot import bot, discord, pymongo
from constants import LINK, DMS_CLOSED_CHANNEL_ID
from datetime import datetime

client = pymongo.MongoClient(LINK, server_api=pymongo.server_api.ServerApi('1'))

class ReactionRolesDB:
    def __init__(self, client):
        self.client = client
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

rrdb = ReactionRolesDB(client)

class PrivateDMThreadDB:
    def __init__(self, client):
        self.client = client
        self.db = self.client.IGCSEBot
        self.dm_threads = self.db["private_dm_threads"]
    
    def new_thread(self, user_id: int, thread_id: int):
        self.dm_threads.insert_one({"_id": str(user_id), "thread_id": str(thread_id)})
        return bot.get_channel(thread_id)
    
    async def del_thread(self, member: discord.Member, thread: discord.Thread):
        self.dm_threads.delete_one({"thread_id": str(thread.id)})
        channel: discord.TextChannel = bot.get_channel(DMS_CLOSED_CHANNEL_ID)
        await channel.set_permissions(
            member,
            overwrite=None
        )
        return thread.delete()
    
    async def get_thread(self, member: discord.Member, create_anyway: bool = True):
        result = self.dm_threads.find_one({"_id": str(member.id)})
        channel: discord.TextChannel = bot.get_channel(DMS_CLOSED_CHANNEL_ID) or await bot.fetch_channel(DMS_CLOSED_CHANNEL_ID)

        if result is None and create_anyway:
            await channel.set_permissions(
                member,
                read_messages=True,
                send_messages=False,
                send_messages_in_threads=True
            )
            thread = await channel.create_thread(name=member.name)
            return self.new_thread(member.id, thread.id)
        elif not create_anyway:
            return None
        else:
            return channel.get_thread(int(result["thread_id"]))

dmsdb = PrivateDMThreadDB(client)

class GuildPreferencesDB:
    def __init__(self, client):
        self.client = client
        self.db = self.client.IGCSEBot
        self.pref = self.db.guild_preferences

    def set_pref(self, pref: str, pref_value, guild_id: int):
        return self.pref.find_one_and_update({"guild_id": guild_id}, {"$set": {pref: pref_value}}, upsert=True)

    def get_pref(self, pref: str, guild_id: int):
        result = self.pref.find_one({"guild_id": guild_id})
        if result is None:
            return None
        else:
            return result.get(pref, None)

gpdb = GuildPreferencesDB(client)


class ReputationDB:
    def __init__(self, client):
        self.client = client
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
        self.reputation.update_one({"user_id": user_id, "guild_id": guild_id}, {"$set": {"rep": new_rep}})
        return new_rep

    def delete_user(self, user_id: int, guild_id: int):
        return self.reputation.delete_one({"user_id": user_id, "guild_id": guild_id})

    def add_rep(self, user_id: int, guild_id: int):
        rep = self.get_rep(user_id, guild_id)
        if rep is None:
            self.reputation.insert_one({"user_id": user_id, "guild_id": guild_id, "rep": 1})
            return 1
        else:
            rep += 1
            self.change_rep(user_id, rep, guild_id)
            return rep

    def rep_leaderboard(self, guild_id):
        leaderboard = self.reputation.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0}).sort("rep", -1)
        return list(leaderboard)


repdb = ReputationDB(client)

class StickyMessageDB:
    def __init__(self, client):
        self.client = client
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

smdb = StickyMessageDB(client)

class KeywordsDB:
    def __init__(self, client):
        self.client = client
        self.db = self.client.IGCSEBot
        self.keywords = self.db.keywords

    def get_keywords(self, guild_id: int):
        result = self.keywords.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0})
        return {i['keyword'].lower(): i['autoreply'] for i in result}
    
    def keyword_list(self, guild_id: int):
        return self.keywords.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0})

    def add_keyword(self, keyword: str, autoreply: str, guild_id: int):
        return self.keywords.insert_one({"keyword": keyword.lower(), "autoreply": autoreply, "guild_id": guild_id})

    def remove_keyword(self, keyword: str, guild_id: int):
        return self.keywords.delete_one({"keyword": keyword.lower(), "guild_id": guild_id})

kwdb = KeywordsDB(client)

class PunishmentsDB:
    def __init__(self, client):
        self.client = client
        self.db = self.client.IGCSEBot
        self.punishment_history = self.db.punishment_history
    
    def add_punishment(self, case_id: int | str, action_against: int, action_by: int, reason: str, action: str, when: datetime = datetime.utcnow(), duration: str = None):
        self.punishment_history.insert_one({
            "case_id": str(case_id),
            "action_against": str(action_against),
            "action_by": str(action_by),
            "reason": reason,
            "action": action,
            "duration": duration,
            "when": when
        })
    
    def get_punishments_by_user(self, user_id: int):
        return self.punishment_history.find({"action_against": str(user_id)})

punishdb = PunishmentsDB(client)

class QuestionsDB:
    def __init__(self, client):
        self.client = client
        self.db = self.client.IGCSEBot
        self.igcse_questions = self.db.igcse_questions
        
    def get_questions(
        self,
        subject_code: str,
        minimum_year: int,
        limit: int,
        topics: list[str],
        type: str = "mcq",
    ):
        if type == "mcq":
            mcq_filter = {
                "$expr": {
                        "$eq": [{"$type": "$answers"}, "string"]
                },
            }
        else:
            mcq_filter = {}
        return self.igcse_questions.aggregate([
            {
                "$match": {
                    "subject": subject_code,
                    "year": {
                        "$gte": minimum_year
                    },
                    "topics": {
                        "$elemMatch": {"$in": topics}
                    },
                    **mcq_filter
                }
            },
            {
                "$sample": {
                    "size": limit
                }
            },
        ])

questionsdb = QuestionsDB(client)