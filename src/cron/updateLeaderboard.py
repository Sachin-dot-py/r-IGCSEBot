import os
import nextcord as discord
from nextcord.ext import commands
import pymongo

intents = discord.Intents().all()
bot = commands.Bot(intents=intents)

TOKEN = os.environ.get("IGCSEBOT_TOKEN")
LINK = os.environ.get("MONGO_LINK")
GUILD_ID = 576460042774118420

class ReputationDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.reputation = self.db.reputation

    def rep_leaderboard(self, guild_id):
        leaderboard = self.reputation.find({"guild_id": guild_id}, {"_id": 0, "guild_id": 0}).sort("rep", -1)
        return list(leaderboard)

repdb = ReputationDB(LINK)

async def update_leaderboard():
    guild = bot.get_guild(GUILD_ID)
    leaderboard = repdb.rep_leaderboard(guild.id)
    members = [list(item.values())[0] for item in leaderboard[:3]]
    role = guild.get_role(862192631261298717)
    if role is None:
        roles = await guild.fetch_roles()
        role = discord.utils.get(roles, id=862192631261298717)
    if [member.id for member in role.members].sort() != members.sort():
        print(f"Leaderboard has changed, updating roles...")
        for m in role.members:
            await m.remove_roles(role)
        for member in members:
            member = guild.get_member(member) or await guild.fetch_member(member)
            await member.add_roles(role)

@bot.event
async def on_ready():
    print("Client ready, updating leaderboard")
    await update_leaderboard()
    print("Leaderboard checked/updated, byeee")
    await bot.close()

bot.run(TOKEN)