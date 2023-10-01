"""
CHANNELLOCK AND FORUMLOCK
commands for the r/IGCSE discord bot
made by discord users:
 - rawr4200
 - juzcallmekaushik

some of the comments have notes (marked with TODO's) so please read them
"""

import nextcord as discord
from nextcord.ext import tasks, commands
import time
from pymongo import MongoClient

TOKEN = ""
GUILD_ID = 1111128710133854289
dbclient = MongoClient("") # TODO replace the DB key
# The format of the database is as follows
# Cluster ⇒ database: "rigcse" ⇒ collection: "channellock" ⇒
# columns: _id: int | channelid: int | unlock: bool | time: int | resolved: bool = False
# if this doesn't match the format of the current db,
#   I have marked the lines which use the database that should be changed with a TODO

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=".", intents=intents)

db = dbclient["rigcse"] # TODO database

async def isModerator(member: discord.Member):
    roles = [role.id for role in member.roles]
    if 1122762930216255612 in roles or 1151522478288552046 in roles:  # TODO - r/igcse moderator role ids
        return True
    elif member.guild_permissions.administrator:
        return True
    return False

async def hasRole(member: discord.Member, role_name: str):
    roles = [role.name.lower() for role in member.roles]
    for role in roles:
        if role_name.lower() in role:
            return True
    return False

@bot.event 
async def on_ready():
  print(f"Logged in as {str(bot.user)}.")
  await bot.change_presence(activity=discord.Game(name="October/November studies T_T")) # TODO probably change this
  checklocks.start() # TODO this needs to be added to the main implementation of on_ready

@bot.event
async def on_message(message:discord.Message):
    message_channel = message.channel.id
    message_content = message.content
    if message_channel == 1153283974211321906: # TODO - #command-logs on our test server
        if message.author.bot: 
            print(message_content)
        else: 
            await message.delete()
    else: 
         return

async def togglechannellock(channelid, unlock, *, unlocktime=0):
    """Function for locking/unlocking a discord channel"""
    guild = bot.get_guild(GUILD_ID)
    everyonerole = guild.get_role(1111128710133854289) # TODO - Role ID for @everyone

    channel = bot.get_channel(channelid)
    overwrite = channel.overwrites_for(everyonerole)
    overwrite.send_messages = unlock

    await channel.set_permissions(everyonerole, overwrite=overwrite)
    await channel.send(f"{'Unl' if unlock else 'L'}ocked channel.")

    if not unlock:
      # If the channel was locked, send another embed with unlock time
      embed = discord.Embed(description=f"Unlocking channel <t:{unlocktime}:R>.")
      await channel.send(embed=embed)

@bot.slash_command(name="channellock", description="Locks a channel at a specified time")
async def lockcommand(interaction: discord.Interaction,
                        channelinput: discord.TextChannel =  discord.SlashOption(name="channel_name", description="Which channel do you want to lock?", required=True),
                        locktime: str = discord.SlashOption(name="lock_time", description="At what time do you want the channel to be locked?", required=True),
                        unlocktime: str = discord.SlashOption(name="unlock_time", description="At what time do you want the channel to be unlocked?", required=True)):

  # perms validation (TODO for testing i've included bot devs in the perms)
  if not await isModerator(interaction.user) or await hasRole(interaction.user, "Bot Developer"):
        await interaction.send(f"Sorry {interaction.user.mention},"
                               "you don't have the permission to perform this action.",
                                ephemeral=True)
        return

  # input validation
  try:
    locktime = int(locktime)
    unlocktime = int(unlocktime)
  except ValueError:
    await interaction.send("Times must be (positive) integers.", ephemeral=True)
    return

  # + 1 is for cancelling the truncation
  t = int(time.time()) + 1
  if locktime < 0 or unlocktime < 0:
    await interaction.send("Lock time must be positive.", ephemeral=True)
    return
  elif locktime >= unlocktime :
    await interaction.send("Unlock time must be after lock time.", ephemeral=True)
    return
  elif unlocktime < t:
    await interaction.send(f"Unlock time has already passed (current time: {round(time.time())}).", ephemeral=True)
    return

  locktimeinunix = f"<t:{locktime}:F>"
  unlocktimeinunix = f"<t:{unlocktime}:F>"
  await interaction.send(f"<#{channelinput.id}> is scheduled to lock on "
                         f"{locktimeinunix} and unlock on {unlocktimeinunix}", ephemeral=True)

  channelid = f"<#{channelinput.id}>"
  logchannel = bot.get_channel(1153283974211321906) # TODO #command-logs again. change
  await logchannel.send(f'Channel Name: {channelid}\n'
                     f'Lock Time: {locktime} ({locktimeinunix})\n'
                     f'Unlock Time: {unlocktime} ({unlocktimeinunix})\n')

  locks = db["channellock"] # TODO collection

  # inserts the lock and unlock as 2 separate entries
  locks.insert_one({"_id": 'l' + str(t), "channelid": channelinput.id,
                     "unlock": False, "time": locktime,
                     "resolved": False})

  locks.insert_one({"_id": 'u' + str(t), "channelid": channelinput.id,
                     "unlock": True, "time": unlocktime,
                     "resolved": False})

  embed = discord.Embed(description=f"Locking channel <t:{max(locktime, t)}:R>.")
  await channelinput.send(embed=embed)

#TODO for now it's at 30s but you might want to change this to be more or less
@tasks.loop(seconds=30)
async def checklocks():
  """Checks the database every 30 seconds to see if anything needs to be locked or unlocked """

  try:
    locks = db["channellock"] # TODO collection
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

bot.run(TOKEN)
